"""LLM-based normalization of resume text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
ResumeSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

from .experience_calculation import (
    calculate_technical_experience_years,
    classify_seniority,
)

PROMPT_KEY = "resume_normalization"


def add_computed_experience_fields(structured_data: dict) -> None:
    """Insert technical_experience_years and calculated_seniority, computed in Python.

    Mutates ``structured_data`` in place. Both values are calculated here
    instead of by the LLM to avoid the model's arithmetic errors when summing
    experience durations (see experience_calculation for details).
    ``calculated_seniority`` is the deterministic seniority band derived from
    ``technical_experience_years``; it is the reliable seniority signal that downstream
    LLM calls (question generation, answer evaluation, study track) reference,
    while the LLM still returns the qualitative ``candidate.llm_estimated_seniority``
    alongside it.
    """
    experiences = structured_data.get("professional_experience") or []
    years = calculate_technical_experience_years(experiences)
    structured_data["technical_experience_years"] = years
    structured_data["calculated_seniority"] = canonicalize_json(classify_seniority(years))


def normalize_resume(text: str) -> dict:
    """Return the normalized resume JSON, or an {"error", "retryable"} dict on failure.

    On success, technical_experience_years and calculated_seniority are
    computed in Python and added to the returned data.
    """
    if not text or not text.strip():
        return {"error": "O texto do currículo está vazio", "retryable": False}

    structured_data = run_prompt_safe(
        PROMPT_KEY,
        {"resume": text},
        missing_prompt_message="Prompt de normalização do currículo não configurado",
    )
    if isinstance(structured_data, dict) and "error" in structured_data:
        return structured_data
    structured_data = canonicalize_json(structured_data)

    # When the LLM flags the text as not a resume it returns only
    # {invalid_input, motivo_invalid_input} with no experiences, so skip
    # the experience computation and let the caller reject the invalid entry.
    if isinstance(structured_data, dict) and not structured_data.get("invalid_input"):
        add_computed_experience_fields(structured_data)
    return structured_data
