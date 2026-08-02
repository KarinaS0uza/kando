"""Views for the ai_core application."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Prompt
from .serializers import PromptSerializer

# During development, permission_classes is IsAuthenticated; switch to
# IsAdminUser before deploying, since prompt edits affect LLM behavior
# app-wide.


class PromptListView(generics.ListAPIView):
    """GET /api/prompts/ — list all prompts."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptCreateView(generics.CreateAPIView):
    """POST /api/prompts/create/ — create a new prompt."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptDetailView(generics.RetrieveAPIView):
    """GET /api/prompts/<pk>/ — retrieve a single prompt."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptUpdateView(generics.UpdateAPIView):
    """PUT/PATCH /api/prompts/<pk>/update/ — update an existing prompt."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]
