"""LLM-based normalization of resume text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
ResumeSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

import json
import os
import time
from string import Template

from groq import Groq

from ai_core.models import Prompt, PromptCallMetadata

from .experience_calculation import (
    calculate_technical_experience_years,
    classify_seniority,
)

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
        formatted_prompt = Template(prompt_row.prompt_detail).safe_substitute(resume=text)
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


def _add_computed_experience_fields(structured_data: dict) -> None:
    """Insert anos_experiencia_tecnica and senioridade_estimada_por_metricas, computed in Python.

    Mutates ``structured_data`` in place. Both values are calculated here
    instead of by the LLM to avoid the model's arithmetic errors when summing
    experience durations (see experience_calculation for details).
    ``senioridade_estimada_por_metricas`` is the deterministic seniority band derived from
    ``anos_experiencia_tecnica``; it is the reliable seniority signal that downstream
    LLM calls (question generation, answer evaluation, study track) reference,
    while the LLM still returns the qualitative ``candidato.senioridade_percebida_pelo_llm``
    alongside it.
    """
    experiences = structured_data.get("experiencias_profissionais") or []
    years = calculate_technical_experience_years(experiences)
    structured_data["anos_experiencia_tecnica"] = years
    structured_data["senioridade_estimada_por_metricas"] = classify_seniority(years)


def normalize_resume(text: str) -> dict:
    """
    Returns the structured JSON from the LLM on success, or
    {"error": str, "retryable": bool} on failure.

    On success, anos_experiencia_tecnica is computed in Python from the LLM output and
    added to the returned data.
    """
    if not text or not text.strip():
        return {"error": "Texto do currículo vazio", "retryable": False}
    try:
        structured_data = _call_llm(text)
    except Prompt.DoesNotExist:
        return {"error": "Prompt de normalização não configurado", "retryable": False}
    except json.JSONDecodeError:
        return {"error": "O LLM retornou um JSON inválido", "retryable": True}
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Service boundary: any failure calling the LLM must degrade to
        # {"error": ...} instead of propagating, so ResumeSubmission creation
        # never breaks because the LLM call failed.
        return {"error": f"Falha ao chamar o LLM: {exc}", "retryable": True}

    # When the LLM flags the text as not a resume it returns only
    # {entrada_invalida, motivo_entrada_invalida} with no experiences, so skip
    # the experience computation and let the caller reject the invalid entry.
    if isinstance(structured_data, dict) and not structured_data.get("entrada_invalida"):
        _add_computed_experience_fields(structured_data)
    return structured_data
