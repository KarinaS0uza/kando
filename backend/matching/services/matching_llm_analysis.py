"""LLM-based compatibility analysis between a resume and a job posting.

Runs on demand, after both the ResumeSubmission and the JobPostingSubmission
have a successful normalization. Requires GROQ_API_KEY in the environment.
"""

import json

from ai_core.llm import run_prompt_safe

PROMPT_KEY = "job_resume_matching_analysis"


def analyze_match(resume_structured_data: dict, job_structured_data: dict) -> dict:
    """Return the match-analysis JSON, or an {"error", "retryable"} dict on failure."""
    variables = {
        "resume": json.dumps(resume_structured_data, ensure_ascii=False),
        "vaga": json.dumps(job_structured_data, ensure_ascii=False),
    }
    return run_prompt_safe(
        PROMPT_KEY,
        variables,
        missing_prompt_message="Prompt de matching não configurado",
    )
