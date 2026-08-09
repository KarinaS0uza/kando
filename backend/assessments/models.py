"""Models for the assessments application."""
import uuid

from django.db import models

from jobs.models import JobPostingSubmission
from resumes.models import ResumeSubmission


class Assessment(models.Model):
    """
    An LLM-generated readiness test for one ResumeSubmission applied to one
    JobPostingSubmission, produced by the assessment generation service.

    Each (resume, job_posting) pair has at most one row: regenerating the
    assessment for the same pair overwrites the existing questions instead of
    creating a new one.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    resume = models.ForeignKey(
        ResumeSubmission,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    job_posting = models.ForeignKey(
        JobPostingSubmission,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    success = models.BooleanField(default=False)
    structured_data = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Full structured JSON (generated questions) returned by the LLM "
            "when success=True."
        ),
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assessment"
        ordering = ["-updated_at"]
        unique_together = [("resume", "job_posting")]
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"

    def __str__(self):
        return f"Assessment({self.resume_id}, {self.job_posting_id}) - success={self.success}"


class AssessmentResult(models.Model):
    """
    The graded outcome of an Assessment, produced by the grading service after
    the candidate answers the generated questions.

    Holds the aggregated score ("nota dos testes") derived from the answers. The
    study track ("trilha de estudos") field is reserved but not yet populated.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name="result",
    )
    success = models.BooleanField(default=False)
    score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=(
            "Aggregated score (0-100) from "
            "structured_data['aggregation']['avaliacao']['score'], promoted "
            "for sorting/filtering."
        ),
    )
    answers = models.JSONField(
        blank=True,
        null=True,
        help_text="Snapshot of the candidate's submitted answers that produced this result.",
    )
    study_track = models.JSONField(
        blank=True,
        null=True,
        help_text=(
            "Reserved for the study track ('trilha de estudos'); not yet "
            "populated by grading."
        ),
    )
    structured_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Full structured JSON returned by the grading LLM when success=True.",
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assessmentresult"
        ordering = ["-created_at"]
        verbose_name = "Assessment Result"
        verbose_name_plural = "Assessment Results"

    def __str__(self):
        return f"AssessmentResult({self.assessment_id}) - success={self.success}"
