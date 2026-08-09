"""Admin registration for the assessments application."""
from django.contrib import admin

from .models import Assessment, AssessmentResult


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for Assessment."""
    list_display = ("id", "resume", "job_posting", "success", "updated_at")
    list_filter = ("success",)


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    """Admin configuration for AssessmentResult."""
    list_display = ("id", "assessment", "success", "score", "created_at")
    list_filter = ("success",)
