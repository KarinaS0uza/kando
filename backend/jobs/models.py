"""Models for the jobs application."""
import uuid

from django.conf import settings
from django.db import models


class JobPosting(models.Model):
    """
    A job posting submitted by a candidate, either as pasted text 
    or as a PDF that will later be processed into text.
    """
    class Source(models.TextChoices):
        """Submission source options for a JobPosting."""
        PDF = "pdf", "PDF"
        TEXT = "text", "Text"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_postings",
        db_column="submitted_by",
    )
    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        help_text="Submission source: 'text' or 'pdf'.",
    )
    raw_text = models.TextField(
        blank=True,
        null=True,
    )

    extracted_text = models.TextField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job_postings"
        ordering = ["-created_at"]
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"

    def __str__(self):
        return f"JobPosting({self.id}) - {self.source}"


class JobPostingNormalization(models.Model):
    """
    Structured data extracted from a JobPosting by the LLM analysis service.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    job_posting = models.OneToOneField(
        JobPosting,
        on_delete=models.CASCADE,
        related_name="normalization",
    )
    success = models.BooleanField(default=False)
    structured_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Full structured JSON returned by the LLM when success=True.",
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job_posting_normalizations"
        ordering = ["-created_at"]
        verbose_name = "Job Posting Normalization"
        verbose_name_plural = "Job Posting Normalizations"

    def __str__(self):
        return f"JobPostingNormalizer({self.job_posting_id}) - success={self.success}"
