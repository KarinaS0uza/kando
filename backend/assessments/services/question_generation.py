"""Generate a readiness assessment from a resume and job posting via the LLM.

Uses the ``question_generation`` prompt; requires GROQ_API_KEY.
"""

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

PROMPT_KEY = "question_generation"

# Bound the single generation call so a hung request cannot stall the view.
REQUEST_TIMEOUT_SECONDS = 60


def build_generation_variables(
    resume_structured_data: dict, job_structured_data: dict
) -> dict:
    """Return the Template substitution values for the generation prompt."""
    candidate = resume_structured_data.get("candidate") or {}
    skills = [
        skill.get("name", "")
        for skill in resume_structured_data.get("technical_skills") or []
    ]
    requirements = job_structured_data.get("required_skills") or []
    return {
        "job_title": (
            job_structured_data.get("job_title")
            or job_structured_data.get("job_posting_title")
            or (job_structured_data.get("vaga") or {}).get("titulo")
            or ""
        ),
        # Prefer the deterministic seniority computed in Python over the LLM's
        # qualitative guess; fall back to the guess for older resumes normalized
        # before calculated_seniority was stored.
        "seniority": (
            resume_structured_data.get("calculated_seniority")
            or candidate.get("llm_estimated_seniority")
            or ""
        ),
        "skills": ", ".join(skills),
        "requirements": (
            ", ".join(requirements)
            if isinstance(requirements, list)
            else str(requirements)
        ),
        "job_area": job_structured_data.get("job_area", ""),
    }


def generate_assessment(resume_structured_data: dict, job_structured_data: dict) -> dict:
    """Return the generated questions JSON, or an {"error", "retryable"} dict on failure."""
    result = run_prompt_safe(
        PROMPT_KEY,
        build_generation_variables(resume_structured_data, job_structured_data),
        missing_prompt_message="Prompt de geração da avaliação não configurado",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if "error" in result:
        return result

    canonical = canonicalize_json(result)
    if not isinstance(canonical, dict) or not isinstance(canonical.get("blocks"), list):
        return {
            "error": "O LLM retornou a avaliação em formato inesperado",
            "retryable": True,
        }
    return canonical
