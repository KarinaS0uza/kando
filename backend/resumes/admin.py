"""Admin registration for the resumes application."""
from django.contrib import admin

from .models import ResumeSubmission, ResumeNormalization


@admin.register(ResumeSubmission)
class ResumeSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for ResumeSubmission."""
    list_display = ("id", "submitted_by", "source", "created_at")
    list_filter = ("source",)


@admin.register(ResumeNormalization)
class ResumeNormalizationAdmin(admin.ModelAdmin):
    """Admin configuration for ResumeNormalization."""
    list_display = ("id", "resume", "success", "created_at")
    list_filter = ("success",)
