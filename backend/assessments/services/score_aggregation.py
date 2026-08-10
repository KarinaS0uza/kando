"""Deterministic scoring and grading orchestration — no LLM calls here.

The overall score is the mean of the valid per-question scores; dimensions and
per-skill scores are aggregated the same way. Failed evaluations (``error`` key)
are ignored. The per-prompt LLM calls live in :mod:`question_generation` and
:mod:`answer_evaluation`.
"""

from .answer_evaluation import evaluate_answer

MAX_HIGHLIGHTS = 5
MAX_SKILL_EVIDENCE = 3

# The evaluation dimensions the LLM scores per question (Portuguese keys are
# part of the question_answer output contract).
DIMENSIONS = ("technical_knowledge", "explanation_clarity", "conceptual_depth")


def to_number(value) -> float:
    """Return ``value`` if it is a real number, else 0.

    Defends the deterministic math against malformed LLM output: a score that
    comes back as a string, ``None``, or a bool would otherwise break ``sum``.
    """
    if isinstance(value, bool):
        return 0
    return value if isinstance(value, (int, float)) else 0


def unique_strings(items: list) -> list:
    """Order-preserving de-duplication that keeps only string items.

    Guards the summary against malformed LLM output where an evidence or
    highlight entry is not a plain string: ``dict.fromkeys`` would otherwise
    raise on an unhashable element (e.g. a dict).
    """
    return list(dict.fromkeys(item for item in items if isinstance(item, str)))


def mean_dimension(valid: list, key: str) -> int:
    """Return the rounded mean of one ``evaluation`` dimension over valid items."""
    values = [to_number(evaluation["evaluation"].get(key)) for evaluation in valid]
    return round(sum(values) / len(values)) if values else 0


def consolidate_skills(valid: list) -> list:
    """Merge the per-question ``skills`` arrays into one score per skill.

    Skills are grouped by ``nome``; each skill's score is the plain mean of its
    per-question scores — including the zeros the LLM assigns when a question's
    answer showed no evidence for that skill, per the question_answer prompt.
    Evidence is deduplicated and capped, and skills are ordered from highest to
    lowest score.
    """
    by_name = {}
    for evaluation in valid:
        skills = evaluation["evaluation"].get("skills")
        if not isinstance(skills, list):
            continue
        for skill in skills:
            if not isinstance(skill, dict):
                continue
            name = skill.get("name")
            if not name:
                continue
            entry = by_name.setdefault(name, {"scores": [], "evidence": []})
            entry["scores"].append(to_number(skill.get("score")))
            evidence = skill.get("evidence")
            if isinstance(evidence, list):
                entry["evidence"].extend(evidence)

    consolidated = [
        {
            "name": name,
            "score": round(sum(data["scores"]) / len(data["scores"])),
            "evidence": unique_strings(data["evidence"])[:MAX_SKILL_EVIDENCE],
        }
        for name, data in by_name.items()
        if data["scores"]
    ]
    consolidated.sort(key=lambda skill: skill["score"], reverse=True)
    return consolidated


def aggregate_evaluations(evaluations: list) -> dict:
    """Combine per-question evaluations into one scored ``evaluation`` summary.

    Each item is an evaluation (``{"evaluation": {...}}``) or a failure
    (``{"error": ...}``); failures are ignored. Score, dimensions, and per-skill
    scores are averaged; strengths/weaknesses are deduplicated and capped.
    """
    valid = [
        evaluation
        for evaluation in evaluations
        if "error" not in evaluation
        and isinstance(evaluation.get("evaluation"), dict)
    ]

    if not valid:
        return {
            "evaluation": {
                "score": 0,
                "technical_knowledge": 0,
                "explanation_clarity": 0,
                "conceptual_depth": 0,
                "skills": [],
                "strengths": [],
                "weaknesses": [],
                "feedback": "No valid evaluations were available.",
            }
        }

    scores = [to_number(evaluation["evaluation"].get("score")) for evaluation in valid]
    mean_score = round(sum(scores) / len(scores))

    strengths = []
    weaknesses = []
    for evaluation in valid:
        item_strengths = evaluation["evaluation"].get("strengths")
        item_weaknesses = evaluation["evaluation"].get("weaknesses")
        if isinstance(item_strengths, list):
            strengths.extend(item_strengths)
        if isinstance(item_weaknesses, list):
            weaknesses.extend(item_weaknesses)

    # Deduplicate preserving order, then cap so the summary stays readable.
    strengths = unique_strings(strengths)[:MAX_HIGHLIGHTS]
    weaknesses = unique_strings(weaknesses)[:MAX_HIGHLIGHTS]

    return {
        "evaluation": {
            "score": mean_score,
            "technical_knowledge": mean_dimension(valid, "technical_knowledge"),
            "explanation_clarity": mean_dimension(valid, "explanation_clarity"),
            "conceptual_depth": mean_dimension(valid, "conceptual_depth"),
            "skills": consolidate_skills(valid),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": (
                f"Average based on {len(valid)} of {len(evaluations)} evaluated questions."
            ),
        }
    }


def resolve_seniority(assessment) -> str:
    """Return the candidate seniority to pass to the evaluation prompt."""
    normalization = getattr(assessment.resume, "normalization", None)
    if not normalization or not normalization.structured_data:
        return ""
    resume_data = normalization.structured_data
    candidate = resume_data.get("candidate") or {}
    # Prefer the deterministic seniority computed in Python; fall back to the
    # LLM's qualitative guess for resumes normalized before
    # calculated_seniority was stored.
    return (
        resume_data.get("calculated_seniority")
        or candidate.get("llm_estimated_seniority")
        or ""
    )


def flatten_questions(structured_data: dict) -> list:
    """Flatten the generated questions from the challenge blocks, in order."""
    questions = []
    for block in structured_data.get("blocks") or []:
        questions.extend(block.get("questions") or [])
    return questions


def grade_assessment(assessment, submitted_answers: list) -> dict:
    """Grade the submitted answers into a dict of AssessmentResult fields.

    Evaluates each question, aggregates deterministically, and returns the
    ``defaults`` for ``AssessmentResult.objects.update_or_create``.

    ``success`` is True only if at least one non-blank answer was graded, so a
    broken prompt (real answers erroring while blanks score 0) can't masquerade
    as a valid score.
    """
    answers_by_id = {answer["id"]: answer["answer"] for answer in submitted_answers}
    questions = flatten_questions(assessment.structured_data or {})
    seniority = resolve_seniority(assessment)

    evaluations = []
    graded_real = False
    for question in questions:
        answer_text = answers_by_id.get(question.get("id"), "")
        evaluation = evaluate_answer(question, answer_text, seniority)
        evaluations.append({"id": question.get("id"), **evaluation})
        if (
            "error" not in evaluation
            and isinstance(evaluation.get("evaluation"), dict)
            and answer_text.strip()
        ):
            graded_real = True

    aggregation = aggregate_evaluations(evaluations)
    structured_data = {"evaluations": evaluations, "aggregation": aggregation}

    if graded_real:
        return {
            "success": True,
            "score": aggregation["evaluation"]["score"],
            "answers": submitted_answers,
            "structured_data": structured_data,
            "error_message": None,
        }
    return {
        "success": False,
        "score": None,
        "answers": submitted_answers,
        "structured_data": structured_data,
        "error_message": "No answer could be evaluated.",
    }
