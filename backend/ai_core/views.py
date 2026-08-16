"""Views for the ai_core application."""

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import Prompt
from .serializers import PromptSerializer


class PromptListView(generics.ListAPIView):
    """List all prompts (admin only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAdminUser]


class PromptCreateView(generics.CreateAPIView):
    """Create (publish) a new prompt (admin only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAdminUser]


class PromptDetailView(generics.RetrieveAPIView):
    """Retrieve a single prompt (admin only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAdminUser]


class PromptUpdateView(generics.UpdateAPIView):
    """Publish an updated version of a prompt (admin only)."""

    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    permission_classes = [IsAdminUser]
