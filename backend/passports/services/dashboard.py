"""Deterministic dashboard aggregation and overall-score calculation.

No LLM calls here — everything is arithmetic over data already produced by
matching and assessments. Reuses the per-skill scores assessments already
consolidated in AssessmentResult.structured_data instead of recomputing them;
only the per-topic ("performance_by_area") breakdown is computed fresh here,
since no other app exposes that view.
"""

TOP_SKILLS_LIMIT = 3

# 40% job compatibility (matching), 60% technical performance (assessment).
WEIGHT_MATCHING = 0.4
WEIGHT_ASSESSMENT = 0.6


def calculate_final_score(match_score: float, assessment_score: float) -> int:
    """Return the weighted overall score (0-100), rounded.

    Deterministic on purpose: the LLM has been observed getting this
    arithmetic wrong, including confusing the 0-100 and 0-1 scales.
    """
    return round((match_score * WEIGHT_MATCHING) + (assessment_score * WEIGHT_ASSESSMENT))


def aggregate_by_topic(assessment_structured_data: dict, evaluations: list) -> dict:
    """Return the mean score per challenge topic/block (e.g. {"React": 75}).

    ``evaluations`` must be in the same order as the flattened questions from
    ``assessment_structured_data["blocks"]``, matching how AssessmentResult
    stores them.
    """
    blocks = assessment_structured_data.get("blocks") or []

    topic_by_position = []
    for block in blocks:
        for _ in block.get("questions") or []:
            topic_by_position.append(block.get("topic"))

    scores_by_topic = {}
    for topic, evaluation in zip(topic_by_position, evaluations):
        if "error" in evaluation or "evaluation" not in evaluation:
            continue
        score = evaluation["evaluation"].get("score", 0)
        scores_by_topic.setdefault(topic, []).append(score)

    return {
        topic: round(sum(scores) / len(scores))
        for topic, scores in scores_by_topic.items()
    }


def extract_performance_by_skill(assessment_result_structured_data: dict) -> dict:
    """Return {skill_name: score}, reusing the skills already consolidated by assessments.

    The source list is already ordered from highest to lowest score by
    assessments/services/score_aggregation.consolidate_skills, and Python
    dicts preserve insertion order, so this stays ordered too.
    """
    skills = (
        (assessment_result_structured_data.get("aggregation") or {})
        .get("evaluation", {})
        .get("skills")
        or []
    )
    return {skill["name"]: skill["score"] for skill in skills if skill.get("name")}


def select_top_skills(skill_scores: dict, limit: int = TOP_SKILLS_LIMIT) -> list:
    """Return the top ``limit`` skills as a display-friendly list."""
    return [
        {"skill": name, "score": score}
        for name, score in list(skill_scores.items())[:limit]
    ]


def generate_summary_feedback(performance_by_area: dict) -> str:
    """Return a short template sentence summarizing strongest/weakest areas.

    Template-based, no LLM call — fully predictable and free.
    """
    valid = {area: score for area, score in performance_by_area.items() if score is not None}

    if not valid:
        return "Ainda não há dados suficientes para gerar um resumo de desempenho."

    if len(valid) == 1:
        area = next(iter(valid))
        return f"Você concluiu a área de {area} com uma pontuação de {valid[area]}%."

    best = max(valid, key=valid.get)
    worst = min(valid, key=valid.get)

    if best == worst:
        return f"Seu desempenho foi consistente em todas as áreas, em torno de {valid[best]}%."

    return (
        f"Você teve um bom desempenho em {best}, mas teve mais dificuldade em {worst}, "
        "o que reduziu sua média."
    )


def build_dashboard_summary(assessment, assessment_result, match_result) -> dict:
    """Return the full dashboard payload for a TalentPassport.

    ``assessment`` supplies the challenge topics, ``assessment_result`` the
    graded evaluations and technical score, ``match_result`` the job
    compatibility score. The overall score is calculated here, not received
    from the caller, so callers never compute it themselves.
    """
    evaluations = (assessment_result.structured_data or {}).get("evaluations") or []
    area_performance = aggregate_by_topic(assessment.structured_data or {}, evaluations)
    best_area = max(area_performance, key=area_performance.get) if area_performance else None

    technical_performance = assessment_result.score or 0
    job_compatibility = match_result.overall_match_score or 0
    final_score = calculate_final_score(job_compatibility, technical_performance)

    skill_performance = extract_performance_by_skill(assessment_result.structured_data or {})

    return {
        "overall_score": final_score,
        "job_compatibility": job_compatibility,
        "technical_performance": technical_performance,
        "best_area": best_area,
        "performance_by_area": area_performance,
        "performance_by_skill": skill_performance,
        "top_skills": select_top_skills(skill_performance),
        "summary_feedback": generate_summary_feedback(area_performance),
    }
