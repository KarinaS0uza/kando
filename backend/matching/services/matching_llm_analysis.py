"""LLM-based compatibility analysis between a resume and a job posting.

Runs on demand, after both the ResumeSubmission and the JobPostingSubmission
have a successful normalization. Requires GROQ_API_KEY in the environment.
"""

import json

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

PROMPT_KEY = "job_resume_matching_analysis"


def analyze_match(resume_structured_data: dict, job_structured_data: dict) -> dict:
    """Return the match-analysis JSON, or an {"error", "retryable"} dict on failure."""
    variables = {
        "resume": json.dumps(resume_structured_data, ensure_ascii=False),
        "job": json.dumps(job_structured_data, ensure_ascii=False),
    }
    result = run_prompt_safe(
        PROMPT_KEY,
        variables,
        missing_prompt_message="Prompt de compatibilidade não configurado",
    )
    if "error" in result:
        return result

    # Canonicalize the response and resolve job_title from whichever key
    # shape is present, so persisted matches have one source of truth.
    result = canonicalize_json(result)
    result["job_title"] = (
        result.get("job_title")
        or result.get("job_posting_title")
        or job_structured_data.get("job_title")
        or job_structured_data.get("job_posting_title")
        or (job_structured_data.get("vaga") or {}).get("titulo")
        or ""
    )
    result.pop("job_posting_title", None)
    return result
