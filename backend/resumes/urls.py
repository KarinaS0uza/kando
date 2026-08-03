"""URLs for the resumes application.

Defines the routes for submitting and privately accessing resumes.
"""
from django.urls import path

from .views import ResumeDetailView, ResumeListCreateView

app_name = "resumes"

urlpatterns = [
    path(
        "resumes/",
        ResumeListCreateView.as_view(),
        name="resume-list-create",
    ),
    path(
        "resumes/<uuid:pk>/",
        ResumeDetailView.as_view(),
        name="resume-detail",
    ),
]
