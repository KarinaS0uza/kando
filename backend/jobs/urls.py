"""URLs for the jobs application.

Defines the routes for submitting and privately accessing job postings.
"""
# urls.py
from django.urls import path

from .views import JobPostingDetailView, JobPostingListCreateView

app_name = "jobs"

urlpatterns = [
    path(
        "job-postings/",
        JobPostingListCreateView.as_view(),
        name="job-posting-list-create",
    ),
    path(
        "job-postings/<uuid:pk>/",
        JobPostingDetailView.as_view(),
        name="job-posting-detail",
    ),
]
