"""Admin registration for the passports application."""
from django.contrib import admin

from .models import CandidatePreparationSelfAssessment, StudyTrack, TalentPassport


@admin.register(TalentPassport)
class TalentPassportAdmin(admin.ModelAdmin):
    """Admin configuration for TalentPassport."""
    list_display = ("id", "user", "resume", "job_posting", "success", "overall_score", "updated_at")
    list_filter = ("success",)
    search_fields = ("user__email", "resume__id", "job_posting__id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudyTrack)
class StudyTrackAdmin(admin.ModelAdmin):
    """Admin configuration for StudyTrack."""
    list_display = ("id", "talent_passport", "success", "title", "created_at")
    list_filter = ("success",)
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CandidatePreparationSelfAssessment)
class CandidatePreparationSelfAssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for CandidatePreparationSelfAssessment."""
    list_display = (
        "id", "user", "resume", "job_posting",
        "perceived_preparation_percentage", "application_threshold_percentage", "created_at",
    )
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")
