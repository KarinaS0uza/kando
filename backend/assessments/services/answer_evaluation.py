"""Evaluate a candidate's answer to one assessment question via the LLM.

Uses the ``question_answer`` prompt, once per answered question; requires
GROQ_API_KEY. Results are combined in :mod:`score_aggregation`.
"""

import json

from ai_core.llm import run_prompt_safe
from ai_core.json_contracts import canonicalize_json

PROMPT_KEY = "question_answer"

# Grading runs one call per answered question, sequentially, inside the request.
# Bound each call so a single hung request cannot stall the whole submission.
REQUEST_TIMEOUT_SECONDS = 30


def build_evaluation_variables(question: dict, answer_text: str, seniority: str) -> dict:
    """Return the Template substitution values for the evaluation prompt."""
    return {
        "question": question.get("prompt", ""),
        "evaluation_criteria": question.get("evaluation_criteria", ""),
        "seniority": seniority,
        "evaluated_skills": json.dumps(
            question.get("evaluated_skills", []), ensure_ascii=False
        ),
        "answer": answer_text,
    }


def evaluate_answer(question: dict, answer_text: str, seniority: str) -> dict:
    """Return the LLM evaluation of one answer, or an {"error", "retryable"} dict.

    A blank answer scores 0 (with 0-score entries for its skills) without
    calling the LLM.
    """
    if not answer_text or not answer_text.strip():
        # A blank answer never reaches the LLM, but the aggregation still needs
        # a 0-score entry for each of this question's skills so the skill's mean
        # reflects the unanswered question instead of silently ignoring it.
        skills = [
            {"name": name, "score": 0, "evidence": []}
            for name in question.get("evaluated_skills") or []
        ]
        return {
            "evaluation": {
                "score": 0,
                "skills": skills,
                "feedback": "Resposta em branco",
            },
            "metadata": {"evaluation_confidence": 1.0},
        }
    result = run_prompt_safe(
        PROMPT_KEY,
        build_evaluation_variables(question, answer_text, seniority),
        missing_prompt_message="Prompt de avaliação de respostas não configurado",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return result if "error" in result else canonicalize_json(result)
