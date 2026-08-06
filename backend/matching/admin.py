"""Admin registration for the matching application."""
from django.contrib import admin

from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    """Admin configuration for MatchResult."""
    list_display = ("id", "resume", "job_posting", "success", "updated_at")
    list_filter = ("success",)
