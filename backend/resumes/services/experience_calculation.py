"""Deterministic computation of experience years and seniority.

These two values are calculated in Python rather than by the LLM: tests showed
the model makes arithmetic errors when summing month durations (e.g. 24 + 18
months yielding "4.5 years" instead of the correct 3.5). The LLM still makes
the qualitative judgment — which experiences count as technical, via the
``conta_como_experiencia_tecnica`` flag — but the final arithmetic is always
done here so the numbers are exact.

The JSON keys (``duracao_meses``, ``conta_como_experiencia_tecnica``) and the
seniority values (``junior``/``pleno``/``senior``/``especialista``) are part of
the LLM output contract and are kept in Portuguese on purpose.
"""


def calculate_technical_experience_years(experiences: list) -> float:
    """Sum the months of technical experiences and convert to years.

    Only experiences the LLM flagged with ``conta_como_experiencia_tecnica``
    are counted; the rest still appear in the resume but do not add to
    technical time. The result is rounded to one decimal place.

    Args:
        experiences (list): The ``experiencias_profissionais`` list from the
            LLM output. Each item may carry ``duracao_meses`` (int months) and
            ``conta_como_experiencia_tecnica`` (bool).

    Returns:
        The total technical experience in years, rounded to one decimal.
    """
    total_months = sum(
        experience.get("duracao_meses", 0) or 0
        for experience in experiences
        if experience.get("conta_como_experiencia_tecnica")
    )
    return round(total_months / 12, 1)


def classify_seniority(years_of_experience: float) -> str:
    """Map years of technical experience to a seniority band.

    Uses the same bands as the rest of the project, now fully deterministic.

    Args:
        years_of_experience (float): Technical experience in years, as returned
            by :func:`calculate_technical_experience_years`.

    Returns:
        One of ``"junior"``, ``"pleno"``, ``"senior"`` or ``"especialista"``.
    """
    if years_of_experience <= 1.5:
        return "junior"
    if years_of_experience <= 4:
        return "pleno"
    if years_of_experience <= 8:
        return "senior"
    return "especialista"
