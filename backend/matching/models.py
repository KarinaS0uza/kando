"""Models for the matching application."""
import uuid

from django.db import models

from jobs.models import JobPostingSubmission
from resumes.models import ResumeSubmission


class MatchResult(models.Model):
    """
    Compatibility analysis between one ResumeSubmission and one
    JobPostingSubmission, produced by the LLM matching service.

    Each (resume, job_posting) pair has at most one row: re-running a match
    for the same pair overwrites the existing result instead of creating a
    new one.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    resume = models.ForeignKey(
        ResumeSubmission,
        on_delete=models.CASCADE,
        related_name="match_results",
    )
    job_posting = models.ForeignKey(
        JobPostingSubmission,
        on_delete=models.CASCADE,
        related_name="match_results",
    )
    success = models.BooleanField(default=False)
    overall_match_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Snapshot of structured_data['score_compatibilidade'], promoted for sorting/filtering.",
    )
    seniority_compatible = models.BooleanField(
        blank=True,
        null=True,
        help_text="Snapshot of structured_data['senioridade_compativel'], promoted for filtering.",
    )
    structured_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Full structured JSON returned by the LLM when success=True.",
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "matchresult"
        ordering = ["-updated_at"]
        unique_together = [("resume", "job_posting")]
        verbose_name = "Match Result"
        verbose_name_plural = "Match Results"

    def __str__(self):
        return f"MatchResult({self.resume_id}, {self.job_posting_id}) - success={self.success}"
