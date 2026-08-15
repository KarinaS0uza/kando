"""Shared LLM call plumbing for prompt-backed services.

Fetches the active Prompt, calls the model, and records a PromptCallMetadata
row. Callers supply the prompt key and the Template substitution values, so each
service keeps its own prompt logic while the call and logging live here, next to
the Prompt and PromptCallMetadata models. Requires GROQ_API_KEY, or GROQ_API_KEYS
(comma-separated) to fall back across multiple keys when one is rate-limited or
rejected.
"""

import json
import logging
import os
import re
import time
from string import Template

from groq import (
    AuthenticationError,
    BadRequestError,
    Groq,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

from .models import Prompt, PromptCallMetadata

logger = logging.getLogger(__name__)

RATE_LIMIT_MAX_WAIT_SECONDS = 10.0
RATE_LIMIT_DEFAULT_WAIT_SECONDS = 2.0
RETRY_AFTER_MESSAGE_PATTERN = re.compile(r"try again in ([\d.]+)s")


def load_api_keys() -> list[str | None]:
    """Return the configured Groq API keys, in fallback order.

    GROQ_API_KEYS (comma-separated) takes precedence; falls back to the
    single GROQ_API_KEY for backward compatibility.
    """
    raw = os.environ.get("GROQ_API_KEYS", "")
    keys = [key.strip() for key in raw.split(",") if key.strip()]
    return keys or [os.environ.get("GROQ_API_KEY")]


API_KEYS = load_api_keys()
clients = [Groq(api_key=key) for key in API_KEYS]
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")


def rate_limit_wait_seconds(exc: RateLimitError) -> float:
    """Return how long to wait before retrying a rate-limited call.

    Reads the standard ``retry-after`` response header first, falling back to
    parsing Groq's "please try again in Xs" message text, and finally a fixed
    default. Capped at RATE_LIMIT_MAX_WAIT_SECONDS so a single call can't hold
    up the caller's request indefinitely.
    """
    header_value = exc.response.headers.get("retry-after") if exc.response is not None else None
    if header_value is not None:
        try:
            return min(float(header_value), RATE_LIMIT_MAX_WAIT_SECONDS)
        except ValueError:
            pass
    match = RETRY_AFTER_MESSAGE_PATTERN.search(str(exc))
    if match:
        return min(float(match.group(1)), RATE_LIMIT_MAX_WAIT_SECONDS)
    return RATE_LIMIT_DEFAULT_WAIT_SECONDS


def create_completion(request_kwargs: dict):
    """Call chat.completions.create, waiting out a rate limit once per key
    before falling back to the next key on a repeated rate-limit or an
    auth/permission error from the current one.
    """
    last_exc: Exception | None = None
    for index, client in enumerate(clients):
        try:
            return client.chat.completions.create(**request_kwargs)
        except RateLimitError as exc:
            wait_seconds = rate_limit_wait_seconds(exc)
            logger.warning(
                "llm: key %d/%d rate limited, waiting %.2fs before retrying",
                index + 1,
                len(clients),
                wait_seconds,
            )
            time.sleep(wait_seconds)
            try:
                return client.chat.completions.create(**request_kwargs)
            except (RateLimitError, AuthenticationError, PermissionDeniedError) as retry_exc:
                last_exc = retry_exc
                if index < len(clients) - 1:
                    logger.warning(
                        "llm: key %d/%d failed again (%s), falling back to next key",
                        index + 1,
                        len(clients),
                        type(retry_exc).__name__,
                    )
        except (AuthenticationError, PermissionDeniedError) as exc:
            last_exc = exc
            if index < len(clients) - 1:
                logger.warning(
                    "llm: key %d/%d failed (%s), falling back to next key",
                    index + 1,
                    len(clients),
                    type(exc).__name__,
                )
    raise last_exc


def run_prompt(
    prompt_key: str, variables: dict, *, timeout: int | None = None, temperature: float = 0.2
) -> dict:
    """Run the active prompt for prompt_key with variables and return parsed JSON.

    Logs a PromptCallMetadata row per call, with a status distinguishing
    missing prompt, invalid JSON, rate limit, config error (auth/permission/
    bad request/not found), and other API errors; re-raises in every case so
    the caller can degrade. When timeout is None the Groq client default is
    used.
    """
    prompt_row = None
    formatted_prompt = ""
    output_text = None
    error_message = None
    usage = None
    status = PromptCallMetadata.Status.API_ERROR
    started_at = time.monotonic()
    try:
        prompt_row = Prompt.objects.get(prompt_description=prompt_key, is_active=True)
        formatted_prompt = Template(prompt_row.prompt_detail).safe_substitute(**variables)
        request_kwargs = {
            "model": MODEL,
            "messages": [{"role": "user", "content": formatted_prompt}],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if timeout is not None:
            request_kwargs["timeout"] = timeout
        response = create_completion(request_kwargs)
        usage = response.usage
        output_text = response.choices[0].message.content
        output_data = json.loads(output_text)
        status = PromptCallMetadata.Status.SUCCESS
        return output_data
    except Prompt.DoesNotExist as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.PROMPT_MISSING
        raise
    except json.JSONDecodeError as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.INVALID_JSON
        raise
    except RateLimitError as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.RATE_LIMITED
        raise
    except (AuthenticationError, PermissionDeniedError, BadRequestError, NotFoundError) as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.CONFIG_ERROR
        raise
    except Exception as exc:
        error_message = str(exc)
        status = PromptCallMetadata.Status.API_ERROR
        raise
    finally:
        PromptCallMetadata.objects.create(
            prompt=prompt_row,
            prompt_description=prompt_row.prompt_description if prompt_row else prompt_key,
            version=prompt_row.version if prompt_row else None,
            model_name=MODEL,
            status=status,
            input_text=formatted_prompt,
            output_text=output_text,
            error_message=error_message,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            duration_ms=int((time.monotonic() - started_at) * 1000),
        )


def run_prompt_safe(
    prompt_key: str, variables: dict, *, missing_prompt_message: str, timeout: int | None = None
) -> dict:
    """Run run_prompt, degrading any failure to an {"error", "retryable"} dict.

    ``missing_prompt_message`` is returned when the prompt is not configured.
    Auth/permission/bad-request/not-found errors are non-retryable config
    issues; rate limits and any other call error are retryable. This is the
    service-boundary entry point: callers never see the LLM exception, so a
    failed call cannot break the surrounding request.
    """
    try:
        return run_prompt(prompt_key, variables, timeout=timeout)
    except Prompt.DoesNotExist:
        return {"error": missing_prompt_message, "retryable": False}
    except json.JSONDecodeError:
        return {"error": "O LLM retornou um JSON inválido", "retryable": True}
    except RateLimitError:
        return {
            "error": "Você atingiu o limite de uso. Tente novamente mais tarde.",
            "retryable": True,
        }
    except (AuthenticationError, PermissionDeniedError, BadRequestError, NotFoundError):
        return {
            "error": "Falha de configuração ao chamar o LLM.",
            "retryable": False,
        }
    except Exception:  # pylint: disable=broad-exception-caught
        return {"error": "Falha ao chamar o LLM.", "retryable": True}
