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
            "version",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "version",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Publish a new version instead of a raw insert (append-only)."""
        prompt = Prompt.publish(
            validated_data["prompt_description"],
            validated_data["prompt_detail"],
            is_active=validated_data.get("is_active", True),
        )[0]
        return prompt

    def update(self, instance, validated_data):
        """An edit publishes a new version of the same prompt; never overwrites.

        The prompt_description is kept from the existing row so the edit stays a
        new version of the same prompt rather than moving it to another key.
        """
        prompt = Prompt.publish(
            instance.prompt_description,
            validated_data.get("prompt_detail", instance.prompt_detail),
            is_active=validated_data.get("is_active", instance.is_active),
        )[0]
        return prompt
