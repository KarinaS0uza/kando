"""LLM-generated professional profile and career recommendations for a Talent Passport.

Combines the resume, match, and assessment analyses already produced by other
apps into one narrative profile. Requires GROQ_API_KEY in the environment.

``proficiency_level`` for each competency is computed here in Python, not by
the LLM, from the resume's per-skill ``confidence_level`` — this keeps the
proficiency scale consistent across candidates instead of depending on the
LLM's own judgment of the scale.
"""

import json
import logging

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

logger = logging.getLogger(__name__)

PROMPT_KEY = "talent_passport_profile"


def classify_proficiency(confidence_level: float) -> str:
    """Return the proficiency band for a resume skill's confidence level (0-1)."""
    if confidence_level <= 0.4:
        return "beginner"
    if confidence_level <= 0.65:
        return "intermediate"
    if confidence_level <= 0.85:
        return "advanced"
    return "expert"


def build_confidence_by_skill(resume_data: dict) -> tuple[dict, dict]:
    """Return (confidence_by_skill, confidence_by_skill_lower) from the resume's skills."""
    confidence_by_skill = {
        skill["name"]: skill.get("confidence_level", 0)
        for skill in resume_data.get("technical_skills", [])
        if skill.get("name")
    }
    confidence_by_skill_lower = {
        name.lower(): value for name, value in confidence_by_skill.items()
    }
    return confidence_by_skill, confidence_by_skill_lower


def attach_proficiency_levels(profile_result: dict, resume_data: dict) -> None:
    """Mutate profile_result in place, adding proficiency_level to each competency.

    Tries an exact skill-name match against the resume first, then a
    case-insensitive match, and only falls back to a neutral default
    confidence as a last resort — logging a warning and marking
    ``confidence_match`` on the competency so a mismatch is visible to callers
    instead of silently producing a misleading proficiency level.
    """
    confidence_by_skill, confidence_by_skill_lower = build_confidence_by_skill(resume_data)

    for competency in profile_result.get("talent_passport", {}).get("competencies", []):
        skill_name = competency.get("skill", "")

        if skill_name in confidence_by_skill:
            confidence = confidence_by_skill[skill_name]
            competency["confidence_match"] = "exact"
        elif skill_name.lower() in confidence_by_skill_lower:
            confidence = confidence_by_skill_lower[skill_name.lower()]
            competency["confidence_match"] = "case_insensitive"
        else:
            confidence = 0.5
            competency["confidence_match"] = "unmatched_fallback"
            logger.warning(
                "profile_recommendations: skill '%s' returned by the LLM in "
                "'competencies' did not match any resume skill name -- using "
                "the default confidence 0.5 (proficiency_level may be "
                "inaccurate). Resume skills available: %s",
                skill_name,
                list(confidence_by_skill.keys()),
            )

        competency["proficiency_level"] = classify_proficiency(confidence)


def generate_professional_profile(
    resume_data: dict, match_data: dict, assessment_data: dict
) -> dict:
    """Return the generated profile JSON, or an {"error", "retryable"} dict on failure."""
    variables = {
        "resume": dump_json(resume_data),
        "matching": dump_json(match_data),
        "evaluation": dump_json(assessment_data),
    }
    result = run_prompt_safe(
        PROMPT_KEY,
        variables,
        missing_prompt_message="Prompt de perfil do Talent Passport não configurado",
    )
    if "error" in result:
        return result

    try:
        result = canonicalize_json(result)
        attach_proficiency_levels(result, resume_data)
    except (AttributeError, TypeError) as exc:
        logger.warning(
            "profile_recommendations: LLM response for '%s' did not match the expected "
            "shape -- degrading to an error result instead of crashing. %s",
            PROMPT_KEY,
            exc,
        )
        return {"error": "O LLM retornou um perfil em formato inesperado", "retryable": True}

    return result


def dump_json(data: dict) -> str:
    """Return data as a compact JSON string for prompt substitution."""
    return json.dumps(data, ensure_ascii=False)
