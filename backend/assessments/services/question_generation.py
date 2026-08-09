"""Generate a readiness assessment from a resume and job posting via the LLM.

Uses the ``question_generation`` prompt; requires GROQ_API_KEY.
"""

from ai_core.llm import run_prompt_safe

PROMPT_KEY = "question_generation"

# Bound the single generation call so a hung request cannot stall the view.
REQUEST_TIMEOUT_SECONDS = 60


def build_generation_variables(
    resume_structured_data: dict, job_structured_data: dict
) -> dict:
    """Return the Template substitution values for the generation prompt."""
    job_details = job_structured_data.get("vaga") or {}
    candidate = resume_structured_data.get("candidato") or {}
    skills = [
        skill.get("nome", "")
        for skill in resume_structured_data.get("skills_tecnicas") or []
    ]
    requirements = job_structured_data.get("requisitos_obrigatorios") or []
    return {
        "cargo": job_details.get("titulo", ""),
        # Prefer the deterministic seniority computed in Python over the LLM's
        # qualitative guess; fall back to the guess for older resumes normalized
        # before senioridade_estimada_por_metricas was stored.
        "senioridade": (
            resume_structured_data.get("senioridade_estimada_por_metricas")
            or candidate.get("senioridade_percebida_pelo_llm")
            or ""
        ),
        "skills": ", ".join(skills),
        "requisitos": (
            ", ".join(requirements)
            if isinstance(requirements, list)
            else str(requirements)
        ),
        "area": job_structured_data.get("area_vaga", ""),
    }


def generate_assessment(resume_structured_data: dict, job_structured_data: dict) -> dict:
    """Return the generated questions JSON, or an {"error", "retryable"} dict on failure."""
    return run_prompt_safe(
        PROMPT_KEY,
        build_generation_variables(resume_structured_data, job_structured_data),
        missing_prompt_message="Prompt de geração de teste não configurado",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
