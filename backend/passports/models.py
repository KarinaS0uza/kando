"""Models for the passports application.

Consolidates the outputs of resumes, jobs, matching, and assessments into
one TalentPassport per (resume, job_posting) flow, plus its personalized
StudyTrack. Also stores CandidatePreparationSelfAssessment, the candidate's
self-reported readiness captured on the waiting screen.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from assessments.models import AssessmentResult
from jobs.models import JobPostingSubmission
from matching.models import MatchResult
from resumes.models import ResumeSubmission


class TalentPassport(models.Model):
    """
    Consolidated Talent Passport for one candidate's application flow,
    produced by the passport generation service from the resume, job
    posting, match result, and assessment result of that flow.

    Each (resume, job_posting) pair has at most one row: regenerating the
    passport for the same pair updates the existing record instead of
    creating a new one.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="talent_passports",
    )
    resume = models.ForeignKey(
        ResumeSubmission,
        on_delete=models.CASCADE,
        related_name="talent_passports",
    )
    job_posting = models.ForeignKey(
        JobPostingSubmission,
        on_delete=models.CASCADE,
        related_name="talent_passports",
    )
    match_result = models.OneToOneField(
        MatchResult,
        on_delete=models.CASCADE,
        related_name="talent_passport",
    )
    assessment_result = models.OneToOneField(
        AssessmentResult,
        on_delete=models.CASCADE,
        related_name="talent_passport",
    )
    success = models.BooleanField(default=False)
    professional_profile = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "LLM-generated professional profile: summary, seniority level, "
            "competencies with a deterministic proficiency level, strengths, "
            "and development areas."
        ),
    )
    career_recommendations = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "LLM-generated suggested roles and learning resources, based on the resume alone."
        ),
    )
    dashboard_summary = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Deterministic dashboard aggregates: score breakdown, performance "
            "by area/skill, feedback."
        ),
    )
    overall_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=(
            "Deterministic weighted score (0-100), promoted from "
            "dashboard_summary for sorting/filtering."
        ),
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "talentpassport"
        ordering = ["-updated_at"]
        unique_together = [("resume", "job_posting")]
        indexes = [
            models.Index(fields=["user", "-updated_at"], name="passport_user_updated_idx"),
        ]
        verbose_name = "Talent Passport"
        verbose_name_plural = "Talent Passports"

    def __str__(self):
        return f"TalentPassport({self.resume_id}, {self.job_posting_id}) - success={self.success}"


class StudyTrack(models.Model):
    """
    Personalized study track for a TalentPassport, produced by the study
    track generation service. Source of truth for the candidate's study
    track; AssessmentResult.study_track is unused.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    talent_passport = models.OneToOneField(
        TalentPassport,
        on_delete=models.CASCADE,
        related_name="study_track",
    )
    success = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True)
    introduction = models.TextField(blank=True)
    items = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Ordered list of study steps, each with position, skill, resource "
            "type/suggestion, and motivational text."
        ),
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "studytrack"
        verbose_name = "Study Track"
        verbose_name_plural = "Study Tracks"

    def __str__(self):
        return f"StudyTrack({self.talent_passport_id}) - success={self.success}"


class CandidatePreparationSelfAssessment(models.Model):
    """
    Candidate's self-reported preparation for one application flow, captured
    on the waiting screen shown right after the resume/job posting are
    submitted. Storage only: the frontend reads these values back for
    display, no comparison or business logic runs on them here.

    Each candidate has at most one row per (resume, job_posting) pair:
    resubmitting updates the existing row instead of creating a new one.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preparation_self_assessments",
    )
    resume = models.ForeignKey(
        ResumeSubmission,
        on_delete=models.CASCADE,
        related_name="preparation_self_assessments",
    )
    job_posting = models.ForeignKey(
        JobPostingSubmission,
        on_delete=models.CASCADE,
        related_name="preparation_self_assessments",
    )
    perceived_preparation_percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How prepared do you feel for this job? (0-100).",
    )
    application_threshold_percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=(
            "What percentage of the job requirements do you believe you should "
            "meet before applying? (0-100)."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidatepreparationselfassessment"
        unique_together = [("user", "resume", "job_posting")]
        verbose_name = "Candidate Preparation Self-Assessment"
        verbose_name_plural = "Candidate Preparation Self-Assessments"

    def __str__(self):
        return (
            f"CandidatePreparationSelfAssessment({self.user_id}, "
            f"{self.resume_id}, {self.job_posting_id})"
        )
