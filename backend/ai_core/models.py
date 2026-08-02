"""Models for the ai_core application."""

import uuid

from django.db import models


class Prompt(models.Model):
    """A reusable LLM prompt template, editable without a code deploy."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    prompt_description = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Unique key used to look up this prompt in code, e.g. 'job_normalization'.",
    )
    prompt_detail = models.TextField(
        help_text="Prompt text, may contain str.format() placeholders.",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Auto-incremented whenever prompt_detail changes.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prompts"
        ordering = ["prompt_description"]
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def save(self, *args, **kwargs):
        if self.pk:
            previous_detail = (
                Prompt.objects.filter(pk=self.pk)
                .values_list("prompt_detail", flat=True)
                .first()
            )
            if previous_detail is not None and previous_detail != self.prompt_detail:
                self.version += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.prompt_description


class PromptCallMetadata(models.Model):
    """Execution metadata for an LLM call made using a Prompt."""

    class Status(models.TextChoices):
        """Possible outcomes of an LLM call."""

        SUCCESS = "success", "Success"
        INVALID_JSON = "invalid_json", "Invalid JSON"
        PROMPT_MISSING = "prompt_missing", "Prompt Missing"
        API_ERROR = "api_error", "API Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.SET_NULL,
        null=True,
        related_name="calls",
    )
    prompt_description = models.SlugField(
        max_length=100,
        help_text="Snapshot of Prompt.prompt_description at call time.",
    )
    version = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Snapshot of Prompt.version at call time.",
    )
    model_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices)
    input_text = models.TextField()
    output_text = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    prompt_tokens = models.PositiveIntegerField(null=True, blank=True)
    completion_tokens = models.PositiveIntegerField(null=True, blank=True)
    total_tokens = models.PositiveIntegerField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "promptcallmetadata"
