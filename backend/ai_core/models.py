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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prompts"
        ordering = ["prompt_description"]
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self):
        return self.prompt_description
