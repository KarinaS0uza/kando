"""LLM-based normalization of job posting text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
JobPostingSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

PROMPT_KEY = "job_normalization"


def canonicalize_job_title(structured_data: dict) -> dict:
    """Store the normalized job title under the canonical ``job_title`` key.

    Accepts multiple possible title key shapes and normalizes them to
    ``job_title``, removing the others so persisted data has one source of
    truth for the title.
    """
    job_details = structured_data.get("job")
    nested_title = job_details.get("title") if isinstance(job_details, dict) else None
    job_title = (
        structured_data.get("job_title")
        or structured_data.get("job_posting_title")
        or nested_title
    )

    structured_data["job_title"] = job_title or ""
    structured_data.pop("job_posting_title", None)
    if isinstance(job_details, dict):
        job_details.pop("title", None)
    return structured_data


def normalize_job_posting(text: str) -> dict:
    """Return the normalized job JSON, or an {"error", "retryable"} dict on failure."""
    if not text or not text.strip():
        return {"error": "O texto da vaga está vazio", "retryable": False}
    result = run_prompt_safe(
        PROMPT_KEY,
        {"job": text},
        missing_prompt_message="Prompt de normalização da vaga não configurado",
    )
    if "error" in result:
        return result
    return canonicalize_job_title(canonicalize_json(result))
