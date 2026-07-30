"""Serializers do app jobs."""
from rest_framework import serializers

from .models import JobPosting

MIN_RAW_TEXT_LENGTH = 150


class JobPostingSerializer(serializers.ModelSerializer):
    # Temporary field used only during the request.
    # It is NOT stored in the database.
    pdf = serializers.FileField(
        write_only=True,
        required=False,
    )

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
        ]
        read_only_fields = [
            "id",
            "submitted_by",
            "extracted_text",
            "created_at",
        ]

    def validate(self, data):
        source = data.get("source")
        raw_text = data.get("raw_text")
        pdf = data.get("pdf")

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

            data["raw_text"] = cleaned

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

        return data

    def create(self, validated_data):
        # Remove the temporary field so Django doesn't try to save it.
        validated_data.pop("pdf", None)

        validated_data["submitted_by"] = self.context["request"].user

        return super().create(validated_data)