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
DIMENSIONS = ("conhecimento_tecnico", "clareza_explicacao", "profundidade_conceitual")


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
    """Return the rounded mean of one ``avaliacao`` dimension over valid items."""
    values = [to_number(evaluation["avaliacao"].get(key)) for evaluation in valid]
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
        skills = evaluation["avaliacao"].get("skills")
        if not isinstance(skills, list):
            continue
        for skill in skills:
            if not isinstance(skill, dict):
                continue
            name = skill.get("nome")
            if not name:
                continue
            entry = by_name.setdefault(name, {"scores": [], "evidence": []})
            entry["scores"].append(to_number(skill.get("score")))
            evidence = skill.get("evidencias")
            if isinstance(evidence, list):
                entry["evidence"].extend(evidence)

    consolidated = [
        {
            "nome": name,
            "score": round(sum(data["scores"]) / len(data["scores"])),
            "evidencias": unique_strings(data["evidence"])[:MAX_SKILL_EVIDENCE],
        }
        for name, data in by_name.items()
        if data["scores"]
    ]
    consolidated.sort(key=lambda skill: skill["score"], reverse=True)
    return consolidated


def aggregate_evaluations(evaluations: list) -> dict:
    """Combine per-question evaluations into one scored ``avaliacao`` summary.

    Each item is an evaluation (``{"avaliacao": {...}}``) or a failure
    (``{"error": ...}``); failures are ignored. Score, dimensions, and per-skill
    scores are averaged; strengths/weaknesses are deduplicated and capped.
    """
    valid = [
        evaluation
        for evaluation in evaluations
        if "error" not in evaluation
        and isinstance(evaluation.get("avaliacao"), dict)
    ]

    if not valid:
        return {
            "avaliacao": {
                "score": 0,
                "conhecimento_tecnico": 0,
                "clareza_explicacao": 0,
                "profundidade_conceitual": 0,
                "skills": [],
                "pontos_fortes": [],
                "pontos_fracos": [],
                "feedback": "Nenhuma avaliação válida",
            }
        }

    scores = [to_number(evaluation["avaliacao"].get("score")) for evaluation in valid]
    mean_score = round(sum(scores) / len(scores))

    strengths = []
    weaknesses = []
    for evaluation in valid:
        pontos_fortes = evaluation["avaliacao"].get("pontos_fortes")
        pontos_fracos = evaluation["avaliacao"].get("pontos_fracos")
        if isinstance(pontos_fortes, list):
            strengths.extend(pontos_fortes)
        if isinstance(pontos_fracos, list):
            weaknesses.extend(pontos_fracos)

    # Deduplicate preserving order, then cap so the summary stays readable.
    strengths = unique_strings(strengths)[:MAX_HIGHLIGHTS]
    weaknesses = unique_strings(weaknesses)[:MAX_HIGHLIGHTS]

    return {
        "avaliacao": {
            "score": mean_score,
            "conhecimento_tecnico": mean_dimension(valid, "conhecimento_tecnico"),
            "clareza_explicacao": mean_dimension(valid, "clareza_explicacao"),
            "profundidade_conceitual": mean_dimension(valid, "profundidade_conceitual"),
            "skills": consolidate_skills(valid),
            "pontos_fortes": strengths,
            "pontos_fracos": weaknesses,
            "feedback": (
                f"Média de {len(valid)} de {len(evaluations)} perguntas avaliadas."
            ),
        }
    }


def resolve_seniority(assessment) -> str:
    """Return the candidate seniority to pass to the evaluation prompt."""
    normalization = getattr(assessment.resume, "normalization", None)
    if not normalization or not normalization.structured_data:
        return ""
    resume_data = normalization.structured_data
    candidate = resume_data.get("candidato") or {}
    # Prefer the deterministic seniority computed in Python; fall back to the
    # LLM's qualitative guess for resumes normalized before
    # senioridade_estimada_por_metricas was stored.
    return (
        resume_data.get("senioridade_estimada_por_metricas")
        or candidate.get("senioridade_percebida_pelo_llm")
        or ""
    )


def flatten_questions(structured_data: dict) -> list:
    """Flatten the generated questions from the challenge blocks, in order."""
    questions = []
    for block in structured_data.get("blocos") or []:
        questions.extend(block.get("perguntas") or [])
    return questions


def grade_assessment(assessment, submitted_answers: list) -> dict:
    """Grade the submitted answers into a dict of AssessmentResult fields.

    Evaluates each question, aggregates deterministically, and returns the
    ``defaults`` for ``AssessmentResult.objects.update_or_create``.

    ``success`` is True only if at least one non-blank answer was graded, so a
    broken prompt (real answers erroring while blanks score 0) can't masquerade
    as a valid score.
    """
    answers_by_id = {answer["id"]: answer["resposta"] for answer in submitted_answers}
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
            and isinstance(evaluation.get("avaliacao"), dict)
            and answer_text.strip()
        ):
            graded_real = True

    aggregation = aggregate_evaluations(evaluations)
    structured_data = {"evaluations": evaluations, "aggregation": aggregation}

    if graded_real:
        return {
            "success": True,
            "score": aggregation["avaliacao"]["score"],
            "answers": submitted_answers,
            "structured_data": structured_data,
            "error_message": None,
        }
    return {
        "success": False,
        "score": None,
        "answers": submitted_answers,
        "structured_data": structured_data,
        "error_message": "Nenhuma resposta pôde ser avaliada.",
    }
