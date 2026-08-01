"""Serializers do app jobs."""
from django.db import transaction
from rest_framework import serializers

from .models import JobPosting, JobPostingNormalization
from .services.job_llm_normalization import normalize_job_posting
from .services.pdf_extraction import PdfExtractionError, extract_text_from_pdf


MIN_RAW_TEXT_LENGTH = 150


class JobPostingNormalizationSerializer(serializers.ModelSerializer):
    """Read-only representation of a JobPosting's LLM normalization result."""

    class Meta:
        model = JobPostingNormalization
        fields = ["success", "structured_data", "error_message", "created_at"]


class JobPostingSerializer(serializers.ModelSerializer):
    """Serializer for creating and reading JobPostings."""

    # Temporary field used only during the request.
    # It is NOT stored in the database.
    pdf = serializers.FileField(
        write_only=True,
        required=False,
    )
    normalization = JobPostingNormalizationSerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "submitted_by",
            "source",
            "raw_text",
            "pdf",
            "extracted_text",
            "created_at",
            "normalization",
        ]
        read_only_fields = [
            "id",
            "submitted_by",
            "extracted_text",
            "created_at",
        ]

    def validate(self, attrs):
        source = attrs.get("source")
        raw_text = attrs.get("raw_text")
        pdf = attrs.get("pdf")

        if source == JobPosting.Source.TEXT:
            if not raw_text or not raw_text.strip():
                raise serializers.ValidationError({
                    "raw_text": "raw_text is required when source='text'."
                })

            if pdf:
                raise serializers.ValidationError({
                    "pdf": "Do not upload a PDF when source='text'."
                })

            cleaned = raw_text.strip()

            if len(cleaned) < MIN_RAW_TEXT_LENGTH:
                raise serializers.ValidationError({
                    "raw_text": f"Minimum {MIN_RAW_TEXT_LENGTH} characters."
                })

            attrs["raw_text"] = cleaned

        elif source == JobPosting.Source.PDF:
            if not pdf:
                raise serializers.ValidationError({
                    "pdf": "A PDF file is required when source='pdf'."
                })

            if raw_text:
                raise serializers.ValidationError({
                    "raw_text": "Do not provide raw_text when source='pdf'."
                })

        else:
            raise serializers.ValidationError({
                "source": "Source must be either 'text' or 'pdf'."
        })

        return attrs

    def create(self, validated_data):
        pdf = validated_data.pop("pdf", None)

        if validated_data.get("source") == JobPosting.Source.PDF:
            try:
                markdown = extract_text_from_pdf(pdf)
            except PdfExtractionError as exc:
                raise serializers.ValidationError({"pdf": str(exc)})
            validated_data["raw_text"] = markdown

        validated_data["submitted_by"] = self.context["request"].user

        normalization_result = normalize_job_posting(validated_data["raw_text"])

        with transaction.atomic():
            job_posting = super().create(validated_data)
            if "error" in normalization_result:
                normalization = JobPostingNormalization.objects.create(
                    job_posting=job_posting,
                    success=False,
                    error_message=normalization_result["error"],
                )
            else:
                normalization = JobPostingNormalization.objects.create(
                    job_posting=job_posting,
                    success=True,
                    structured_data=normalization_result,
                )

        job_posting.normalization = normalization
        return job_posting
