"""Models for the ai_core application."""

import uuid

from django.db import models, transaction


class Prompt(models.Model):
    """A reusable LLM prompt template, editable without a code deploy."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    prompt_description = models.SlugField(
        max_length=100,
        db_index=True,
        help_text=(
            "Key used to look up this prompt in code, e.g. 'job_normalization'. "
            "Not unique on its own: every edit adds a new version row under the "
            "same key, so multiple rows share a prompt_description."
        ),
    )
    prompt_detail = models.TextField(
        help_text="Prompt text, may contain string.Template placeholders.",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text=(
            "Version number of this prompt. A new row (version + 1) is created "
            "on every change; existing versions are never overwritten."
        ),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prompts"
        ordering = ["prompt_description", "-version"]
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"
        constraints = [
            models.UniqueConstraint(
                fields=["prompt_description", "version"],
                name="unique_prompt_description_version",
            ),
            models.UniqueConstraint(
                fields=["prompt_description"],
                condition=models.Q(is_active=True),
                name="unique_active_prompt_per_description",
            ),
        ]

    @classmethod
    def publish(cls, prompt_description, prompt_detail, *, is_active=True):
        """Store a prompt as a new immutable version, never overwriting old ones.

        If the latest version for ``prompt_description`` already holds the exact
        same ``prompt_detail``, no new row is created. Otherwise a row is
        inserted with ``version`` one higher than the current latest. When
        ``is_active`` is true the new version becomes the sole active one for
        this description (any previously active version is deactivated first).

        Returns ``(prompt, created)``.
        """
        with transaction.atomic():
            latest = (
                cls.objects.select_for_update()
                .filter(prompt_description=prompt_description)
                .order_by("-version")
                .first()
            )
            unchanged = latest is not None and latest.prompt_detail == prompt_detail
            if unchanged and (latest.is_active or not is_active):
                return latest, False
            if is_active:
                cls.objects.filter(
                    prompt_description=prompt_description, is_active=True
                ).update(is_active=False)
            if unchanged:
                latest.is_active = True
                latest.save(update_fields=["is_active"])
                return latest, False
            next_version = (latest.version + 1) if latest else 1
            prompt = cls.objects.create(
                prompt_description=prompt_description,
                prompt_detail=prompt_detail,
                version=next_version,
                is_active=is_active,
            )
            return prompt, True

    def __str__(self):
        return f"{self.prompt_description} (v{self.version})"


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
