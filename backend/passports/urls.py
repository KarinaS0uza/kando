"""URLs for the passports application.

Defines the routes for generating and privately accessing Talent Passports,
and for the candidate's preparation self-assessment.
"""
from django.urls import path

from .views import (
    CandidatePreparationSelfAssessmentView,
    TalentPassportDetailView,
    TalentPassportListCreateView,
)

app_name = "passports"

urlpatterns = [
    path(
        "passports/",
        TalentPassportListCreateView.as_view(),
        name="passport-list-create",
    ),
    path(
        "passports/<uuid:pk>/",
        TalentPassportDetailView.as_view(),
        name="passport-detail",
    ),
    path(
        "passports/waiting-readiness/",
        CandidatePreparationSelfAssessmentView.as_view(),
        name="waiting-readiness",
    ),
]
