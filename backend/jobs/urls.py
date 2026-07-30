"""URLs do app jobs.

Define as rotas de envio e acesso privado a vagas.
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
