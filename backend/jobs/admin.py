"""Admin do app jobs."""
from django.contrib import admin

from .models import JobPosting, JobPostingNormalization


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    """Admin da JobPosting."""
    list_display = ("id", "submitted_by", "source", "created_at")
    list_filter = ("source",)


@admin.register(JobPostingNormalization)
class JobPostingNormalizationAdmin(admin.ModelAdmin):
    """Admin da JobPostingNormalization."""
    list_display = ("id", "job_posting", "success", "created_at")
    list_filter = ("success",)
