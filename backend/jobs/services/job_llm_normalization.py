"""LLM-based normalization of job posting text (extraction/normalization step).

Runs after text extraction (PDF via docling, or plain text), before the
JobPostingSubmission is persisted. Requires GROQ_API_KEY in the environment.
"""

from ai_core.llm import run_prompt_safe

PROMPT_KEY = "job_normalization"


def normalize_job_posting(text: str) -> dict:
    """Return the normalized job JSON, or an {"error", "retryable"} dict on failure."""
    if not text or not text.strip():
        return {"error": "Texto da vaga vazio", "retryable": False}
    return run_prompt_safe(
        PROMPT_KEY,
        {"vaga": text},
        missing_prompt_message="Prompt de normalização não configurado",
    )
