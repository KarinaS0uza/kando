"""LLM-based normalization of resume text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
ResumeSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

from ai_core.llm import run_prompt_safe

from .experience_calculation import (
    calculate_technical_experience_years,
    classify_seniority,
)

PROMPT_KEY = "resume_normalization"


def add_computed_experience_fields(structured_data: dict) -> None:
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
    """Return the normalized resume JSON, or an {"error", "retryable"} dict on failure.

    On success, anos_experiencia_tecnica and senioridade_estimada_por_metricas are
    computed in Python and added to the returned data.
    """
    if not text or not text.strip():
        return {"error": "Texto do currículo vazio", "retryable": False}

    structured_data = run_prompt_safe(
        PROMPT_KEY,
        {"resume": text},
        missing_prompt_message="Prompt de normalização não configurado",
    )
    if isinstance(structured_data, dict) and "error" in structured_data:
        return structured_data

    # When the LLM flags the text as not a resume it returns only
    # {entrada_invalida, motivo_entrada_invalida} with no experiences, so skip
    # the experience computation and let the caller reject the invalid entry.
    if isinstance(structured_data, dict) and not structured_data.get("entrada_invalida"):
        add_computed_experience_fields(structured_data)
    return structured_data
