"""LLM-based normalization of resume text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
ResumeSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

import json
import os
import time

from groq import Groq

from ai_core.models import Prompt, PromptCallMetadata

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

PROMPT_KEY = "resume_normalization"


def _call_llm(text: str) -> dict:
    prompt_row = None
    formatted_prompt = ""
    output_text = None
    error_message = None
    usage = None
    status = PromptCallMetadata.Status.API_ERROR
    started_at = time.monotonic()
    try:
        prompt_row = Prompt.objects.get(prompt_description=PROMPT_KEY, is_active=True)
        formatted_prompt = prompt_row.prompt_detail.format(resume=text)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
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
            prompt_description=prompt_row.prompt_description if prompt_row else PROMPT_KEY,
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


def normalize_resume(text: str) -> dict:
    """
    Returns the structured JSON from the LLM on success, or
    {"error": str, "retryable": bool} on failure.
    """
    if not text or not text.strip():
        return {"error": "Texto do currículo vazio", "retryable": False}
    try:
        return _call_llm(text)
    except Prompt.DoesNotExist:
        return {"error": "Prompt de normalização não configurado", "retryable": False}
    except json.JSONDecodeError:
        return {"error": "O LLM retornou um JSON inválido", "retryable": True}
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Service boundary: any failure calling the LLM must degrade to
        # {"error": ...} instead of propagating, so ResumeSubmission creation
        # never breaks because the LLM call failed.
        return {"error": f"Falha ao chamar o LLM: {exc}", "retryable": True}
