"""Talent Passport generation workflow orchestration.

Validates ownership and upstream data, builds the deterministic dashboard and
overall score, generates the professional profile and study track, and
upserts the TalentPassport/StudyTrack rows in one transaction. Consolidates
existing results from resumes, jobs, matching, and assessments — it does not
recompute or duplicate any of their source data.
"""

from dataclasses import dataclass

from django.db import transaction

from assessments.models import Assessment, AssessmentResult
from jobs.models import JobPostingNormalization
from matching.models import MatchResult
from resumes.models import ResumeNormalization

from . import dashboard, profile_recommendations, study_track
from ..models import StudyTrack, TalentPassport


class PassportGenerationError(Exception):
    """Raised when a Talent Passport cannot be generated for the given inputs."""


@dataclass(frozen=True)
class UpstreamRecords:
    """Validated records required to generate a Talent Passport."""

    resume_normalization: ResumeNormalization
    job_normalization: JobPostingNormalization
    match_result: MatchResult
    assessment: Assessment
    assessment_result: AssessmentResult


@dataclass(frozen=True)
class ProfileFields:
    """Profile output split according to the TalentPassport model fields."""

    success: bool
    professional_profile: dict | None
    career_recommendations: dict | None
    error: str | None


def resolve_upstream_records(user, resume, job_posting):
    """Return the validated records needed for passport generation.

    Raises PassportGenerationError with a clear message when ownership is
    wrong or any required upstream record is missing or unsuccessful.
    """
    if resume.submitted_by_id != user.id or job_posting.submitted_by_id != user.id:
        raise PassportGenerationError("Currículo ou vaga não encontrados.")

    resume_normalization = getattr(resume, "normalization", None)
    if not resume_normalization or not resume_normalization.success:
        raise PassportGenerationError("O currículo ainda não foi normalizado com sucesso.")

    job_normalization = getattr(job_posting, "normalization", None)
    if not job_normalization or not job_normalization.success:
        raise PassportGenerationError("A vaga ainda não foi normalizada com sucesso.")

    match_result = MatchResult.objects.filter(resume=resume, job_posting=job_posting).first()
    if not match_result or not match_result.success:
        raise PassportGenerationError(
            "A compatibilidade entre currículo e vaga ainda não foi gerada com sucesso."
        )

    assessment = (
        Assessment.objects.filter(resume=resume, job_posting=job_posting)
        .select_related("result")
        .first()
    )
    if not assessment or not assessment.success:
        raise PassportGenerationError("A avaliação técnica ainda não foi gerada com sucesso.")

    assessment_result = getattr(assessment, "result", None)
    if not assessment_result or not assessment_result.success:
        raise PassportGenerationError("A avaliação técnica ainda não foi corrigida com sucesso.")

    return UpstreamRecords(
        resume_normalization=resume_normalization,
        job_normalization=job_normalization,
        match_result=match_result,
        assessment=assessment,
        assessment_result=assessment_result,
    )


def build_profile_fields(profile_result: dict) -> ProfileFields:
    """Split the LLM result into fields stored by TalentPassport.

    Returns all-None values with success=False when the LLM call failed,
    instead of fabricating profile content.
    """
    if "error" in profile_result:
        return ProfileFields(False, None, None, profile_result["error"])

    final = profile_result.get("talent_passport", {})
    professional_profile = {
        "professional_summary": final.get("professional_summary"),
        "overall_level": final.get("overall_level"),
        "competencies": final.get("competencies", []),
        "strengths": final.get("strengths", []),
        "development_areas": final.get("development_areas", []),
        "metadata": profile_result.get("metadata", {}),
    }
    career_recommendations = {
        "suggested_roles": final.get("suggested_roles", []),
        "suggested_resources": final.get("suggested_resources", []),
    }
    return ProfileFields(
        success=True,
        professional_profile=professional_profile,
        career_recommendations=career_recommendations,
        error=None,
    )


def build_study_track_input(
    records: UpstreamRecords,
    profile_fields: ProfileFields,
    dashboard_summary: dict,
) -> study_track.StudyTrackInput:
    """Build study-track inputs from validated upstream and profile data."""
    role, seniority = resolve_role_and_seniority(
        records.job_normalization, records.resume_normalization
    )
    professional_profile = profile_fields.professional_profile or {}
    career_recommendations = profile_fields.career_recommendations or {}
    return study_track.StudyTrackInput(
        role=role,
        seniority=seniority,
        missing_skills=(records.match_result.structured_data or {}).get("missing_skills", []),
        development_areas=professional_profile.get("development_areas", []),
        suggested_resources=career_recommendations.get("suggested_resources", []),
        performance_by_skill=dashboard_summary["performance_by_skill"],
    )


def resolve_role_and_seniority(job_normalization, resume_normalization) -> tuple[str, str]:
    """Return (role, seniority) used to personalize the study track narrative."""
    job_data = job_normalization.structured_data or {}
    resume_data = resume_normalization.structured_data or {}
    candidate = resume_data.get("candidate") or {}
    # ``job_title`` is the canonical field; the other lookups are fallbacks
    # for normalized records that don't have it set.
    role = (
        job_data.get("job_title")
        or job_data.get("job_posting_title")
        or (job_data.get("vaga") or {}).get("titulo")
        or "a vaga"
    )
    seniority = (
        resume_data.get("calculated_seniority") or candidate.get("llm_estimated_seniority") or ""
    )
    return role, seniority


@transaction.atomic
def generate_talent_passport(user, resume, job_posting) -> tuple[TalentPassport, bool]:
    """Generate or refresh the TalentPassport for one (resume, job_posting) flow.

    Returns (passport, created). Idempotent: calling this again for the same
    pair updates the existing TalentPassport/StudyTrack rows instead of
    creating duplicates.
    """
    records = resolve_upstream_records(user, resume, job_posting)

    dashboard_summary = dashboard.build_dashboard_summary(
        records.assessment, records.assessment_result, records.match_result
    )

    profile_result = profile_recommendations.generate_professional_profile(
        records.resume_normalization.structured_data,
        records.match_result.structured_data,
        records.assessment_result.structured_data,
    )
    profile_fields = build_profile_fields(profile_result)
    study_track_result = study_track.generate_study_track(
        build_study_track_input(records, profile_fields, dashboard_summary)
    )

    passport, created = TalentPassport.objects.update_or_create(
        resume=resume,
        job_posting=job_posting,
        defaults={
            "user": user,
            "match_result": records.match_result,
            "assessment_result": records.assessment_result,
            "success": profile_fields.success,
            "professional_profile": profile_fields.professional_profile,
            "career_recommendations": profile_fields.career_recommendations,
            "dashboard_summary": dashboard_summary,
            "overall_score": dashboard_summary["overall_score"],
            "error_message": profile_fields.error,
        },
    )

    StudyTrack.objects.update_or_create(
        talent_passport=passport,
        defaults={
            "success": study_track_result["success"],
            "title": (
                study_track_result.get("study_track_title")
                or study_track_result.get("skill_track_title")
                or study_track_result.get("titulo_trilha", "")
            ),
            "introduction": study_track_result.get("introduction", ""),
            "items": study_track_result.get("items", []),
            "error_message": study_track_result.get("narrative_error"),
        },
    )

    return passport, created
