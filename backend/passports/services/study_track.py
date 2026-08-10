"""Personalized study track generation for a Talent Passport.

Combines data already produced by other apps (matching, profile
recommendations, dashboard) — it does not invent a new skill or resource.
Priority order is computed here in Python, deterministically; the LLM only
writes the motivational narrative connecting the steps, without reordering or
inventing resources. Requires GROQ_API_KEY in the environment.
"""

import json
import logging
from dataclasses import dataclass

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

logger = logging.getLogger(__name__)

PROMPT_KEY = "talent_passport_study_track"


@dataclass(frozen=True)
class StudyTrackInput:
    """Structured inputs needed to build a candidate's study track."""

    role: str
    seniority: str
    missing_skills: list
    development_areas: list
    suggested_resources: list
    performance_by_skill: dict | None = None


def calculate_skill_priority(
    missing_skills: list,
    development_areas: list,
    performance_by_skill: dict | None = None,
) -> list:
    """Return skills ordered by study priority, deterministically.

    Scoring: +2 for a skill in missing_skills (matching gap), +1 for a skill
    in development_areas (profile), +2 more if that skill's performance is
    below 50. The performance lookup is by exact skill name (case-insensitive)
    only — never by substring — since matching a skill against an unrelated
    topic/block name would silently misattribute the performance bonus.
    """
    priority = {}

    for skill in missing_skills:
        priority[skill] = priority.get(skill, 0) + 2

    for skill in development_areas:
        priority[skill] = priority.get(skill, 0) + 1

    if performance_by_skill:
        scores_lower = {name.lower(): score for name, score in performance_by_skill.items()}
        for skill in priority:
            score = scores_lower.get(skill.lower())
            if score is not None and score < 50:
                priority[skill] += 2

    return sorted(priority, key=priority.get, reverse=True)


def build_base_study_track(ordered_skills: list, suggested_resources: list) -> list:
    """Pair each ordered skill with the resource already suggested for it.

    Skills with no matching suggested resource still appear in the track,
    with resource_type/resource_suggestion set to None.
    """
    resources_by_skill = {resource["related_skill"]: resource for resource in suggested_resources}

    track = []
    for position, skill in enumerate(ordered_skills, start=1):
        resource = resources_by_skill.get(skill)
        track.append(
            {
                "position": position,
                "skill": skill,
                "resource_type": resource["type"] if resource else None,
                "resource_suggestion": resource["suggestion"] if resource else None,
            }
        )
    return track


def generate_study_track_narrative(role: str, seniority: str, base_track: list) -> dict:
    """Return the LLM-written narrative for the base track, or an {"error", ...} dict."""
    variables = {
        "job_title": role,
        "seniority": seniority,
        "base_track": json.dumps(base_track, ensure_ascii=False),
    }
    result = run_prompt_safe(
        PROMPT_KEY,
        variables,
        missing_prompt_message="Prompt da trilha de estudos não configurado",
    )
    return result if "error" in result else canonicalize_json(result)


def generate_study_track(track_input: StudyTrackInput) -> dict:
    """Return the complete study track: deterministic order + LLM narrative.

    Always succeeds at producing a usable track: when there is no gap to
    study the track is empty, and when the narrative LLM call fails the track
    still has its items and priority order, just without motivational copy
    (``narrative_error`` is set in that case so the caller can surface it).
    """
    ordered_skills = calculate_skill_priority(
        track_input.missing_skills,
        track_input.development_areas,
        track_input.performance_by_skill,
    )
    base_track = build_base_study_track(ordered_skills, track_input.suggested_resources)

    if not base_track:
        return {
            "success": True,
            "study_track_title": "Nenhuma lacuna de habilidade identificada",
            "introduction": "No momento não há áreas de desenvolvimento pendentes.",
            "items": [],
            "narrative_error": None,
        }

    narrative = generate_study_track_narrative(track_input.role, track_input.seniority, base_track)
    narrative_error = narrative.get("error") if "error" in narrative else None

    motivation_by_position = {}
    if not narrative_error:
        try:
            motivation_by_position = {
                item.get("position"): item.get("motivation", "")
                for item in narrative.get("items", [])
            }
        except AttributeError as exc:
            logger.warning(
                "study_track: LLM narrative for '%s' did not match the expected shape -- "
                "falling back to the track without motivational copy. %s",
                PROMPT_KEY,
                exc,
            )
            narrative_error = "O LLM retornou uma trilha de estudos em formato inesperado"

    if narrative_error:
        narrative = {
            "study_track_title": f"Trilha de estudos para {track_input.role}",
            "introduction": "Sugestões baseadas nas áreas de maior prioridade identificadas.",
            "items": [
                {"position": item["position"], "skill": item["skill"], "motivation": ""}
                for item in base_track
            ],
        }
        motivation_by_position = {
            item["position"]: item["motivation"] for item in narrative["items"]
        }

    for item in base_track:
        item["motivation"] = motivation_by_position.get(item["position"], "")

    return {
        "success": True,
        "study_track_title": (
            narrative.get("study_track_title")
            or narrative.get("skill_track_title")
            or narrative.get("titulo_trilha")
            or f"Trilha de estudos para {track_input.role}"
        ),
        "introduction": narrative.get("introduction", ""),
        "items": base_track,
        "narrative_error": narrative_error,
    }
