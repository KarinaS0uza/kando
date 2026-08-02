"""Serializers for the ai_core application."""

from rest_framework import serializers

from .models import Prompt


class PromptSerializer(serializers.ModelSerializer):
    """Serialize Prompt instances for reading and writing."""

    class Meta:
        """Configure writable, readable, and protected model fields."""

        model = Prompt
        fields = [
            "id",
            "prompt_description",
            "prompt_detail",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
