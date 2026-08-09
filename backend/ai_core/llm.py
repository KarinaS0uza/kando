"""Shared LLM call plumbing for prompt-backed services.

Fetches the active Prompt, calls the model, and records a PromptCallMetadata
row. Callers supply the prompt key and the Template substitution values, so each
service keeps its own prompt logic while the call and logging live here, next to
the Prompt and PromptCallMetadata models. Requires GROQ_API_KEY.
"""

import json
import os
import time
from string import Template

from groq import Groq

from .models import Prompt, PromptCallMetadata

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def run_prompt(
    prompt_key: str, variables: dict, *, timeout: int | None = None, temperature: float = 0.2
) -> dict:
    """Run the active prompt for prompt_key with variables and return parsed JSON.

    Logs a PromptCallMetadata row per call; re-raises on missing prompt,
    invalid JSON, or API error so the caller can degrade. When timeout is None
    the Groq client default is used.
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
        response = client.chat.completions.create(**request_kwargs)
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

    ``missing_prompt_message`` is returned when the prompt is not configured; a
    generic message covers invalid JSON or any other call error. This is the
    service-boundary entry point: callers never see the LLM exception, so a
    failed call cannot break the surrounding request.
    """
    try:
        return run_prompt(prompt_key, variables, timeout=timeout)
    except Prompt.DoesNotExist:
        return {"error": missing_prompt_message, "retryable": False}
    except json.JSONDecodeError:
        return {"error": "O LLM retornou um JSON inválido", "retryable": True}
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return {"error": f"Falha ao chamar o LLM: {exc}", "retryable": True}
