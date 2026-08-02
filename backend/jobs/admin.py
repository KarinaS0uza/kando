"""Admin registration for the jobs application."""
from django.contrib import admin

from .models import JobPostingSubmission, JobPostingNormalization


@admin.register(JobPostingSubmission)
class JobPostingAdmin(admin.ModelAdmin):
    """Admin configuration for JobPostingSubmission."""
    list_display = ("id", "submitted_by", "source", "created_at")
    list_filter = ("source",)


@admin.register(JobPostingNormalization)
class JobPostingNormalizationAdmin(admin.ModelAdmin):
    """Admin configuration for JobPostingNormalization."""
    list_display = ("id", "job_posting", "success", "created_at")
    list_filter = ("success",)
