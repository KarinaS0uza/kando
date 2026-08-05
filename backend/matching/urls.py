"""URLs for the matching application.

Defines the routes for requesting and privately accessing match results.
"""
from django.urls import path

from .views import MatchDetailView, MatchListCreateView

app_name = "matching"

urlpatterns = [
    path(
        "matching/",
        MatchListCreateView.as_view(),
        name="match-list-create",
    ),
    path(
        "matching/<uuid:pk>/",
        MatchDetailView.as_view(),
        name="match-detail",
    ),
]
