"""URLs for the assessments application.

Defines the routes for generating and privately accessing assessments.
"""
from django.urls import path

from .views import (
    AssessmentDetailView,
    AssessmentListCreateView,
    AssessmentResultCreateView,
)

app_name = "assessments"

urlpatterns = [
    path(
        "assessments/",
        AssessmentListCreateView.as_view(),
        name="assessment-list-create",
    ),
    path(
        "assessments/<uuid:pk>/",
        AssessmentDetailView.as_view(),
        name="assessment-detail",
    ),
    path(
        "assessments/<uuid:pk>/result/",
        AssessmentResultCreateView.as_view(),
        name="assessment-result-create",
    ),
]
