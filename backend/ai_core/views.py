"""Views for the ai_core application."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Prompt
from .serializers import PromptSerializer

# During development, permission_classes is IsAuthenticated; switch to
# IsAdminUser before deploying, since prompt edits affect LLM behavior
# app-wide.


class PromptListView(generics.ListAPIView):
    """List all prompts (authenticated only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptCreateView(generics.CreateAPIView):
    """Create (publish) a new prompt (authenticated only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptDetailView(generics.RetrieveAPIView):
    """Retrieve a single prompt (authenticated only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]


class PromptUpdateView(generics.UpdateAPIView):
    """Publish an updated version of a prompt (authenticated only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated]
