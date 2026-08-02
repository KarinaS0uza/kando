"""URLs for the ai_core application."""

from django.urls import path

from .views import (
    PromptCreateView,
    PromptDetailView,
    PromptListView,
    PromptUpdateView,
)

app_name = "ai_core"

urlpatterns = [
    path(
        "prompts/",
        PromptListView.as_view(),
        name="prompt-list",
    ),
    path(
        "prompts/create/",
        PromptCreateView.as_view(),
        name="prompt-create",
    ),
    path(
        "prompts/<uuid:pk>/",
        PromptDetailView.as_view(),
        name="prompt-detail",
    ),
    path(
        "prompts/<uuid:pk>/update/",
        PromptUpdateView.as_view(),
        name="prompt-update",
    ),
]
