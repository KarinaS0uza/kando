"""Serializers and input validation for the jobs application."""

from rest_framework import serializers

from .models import JobPostingSubmission, JobPostingNormalization


MIN_RAW_TEXT_LENGTH = 150
MAX_RAW_TEXT_LENGTH = 100_000

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB
PDF_SIGNATURE = b"%PDF-"


def validate_job_text(text):
    """Validate and clean job-posting text.

    This function is shared by manually submitted text and text extracted
    from PDF files. It removes surrounding whitespace and enforces the
    minimum and maximum character limits.

    Args:
        text (str): Job-posting text submitted by the user or extracted
            from a PDF.

    Returns:
        The validated text without surrounding whitespace.

    Raises:
        serializers.ValidationError: When the text is empty, too short,
            or exceeds the maximum allowed length.
    """
    if not text or not text.strip():
        raise serializers.ValidationError(
            "O texto da vaga não pode estar vazio."
        )

    cleaned_text = text.strip()

    if len(cleaned_text) < MIN_RAW_TEXT_LENGTH:
        raise serializers.ValidationError(
            f"A vaga deve ter no mínimo "
            f"{MIN_RAW_TEXT_LENGTH} caracteres."
        )

    if len(cleaned_text) > MAX_RAW_TEXT_LENGTH:
        raise serializers.ValidationError(
            f"A vaga não pode exceder "
            f"{MAX_RAW_TEXT_LENGTH} caracteres."
        )

    return cleaned_text


class JobPostingNormalizationSerializer(serializers.ModelSerializer):
    """Serialize the result produced by the LLM normalization service.

    This serializer is read-only because normalization data is generated
    internally by the application, not submitted directly by the frontend.
    """

    class Meta:
        """Configure the normalization model representation."""

        model = JobPostingNormalization
        fields = [
            "success",
            "structured_data",
            "error_message",
            "created_at",
        ]
        read_only_fields = fields


class JobPostingSerializer(serializers.ModelSerializer):
    """Serialize job postings and validate text or PDF submissions.

    A job posting must be submitted using exactly one source:

    - ``text`` requires ``raw_text`` and does not accept a PDF.
    - ``pdf`` requires a PDF and does not accept ``raw_text``.

    PDF files are accepted only during writes and are not included in API
    responses. Normalization results are included only as read-only data.
    """

    pdf = serializers.FileField(
        write_only=True,
        required=False,
    )

    normalization = JobPostingNormalizationSerializer(
        read_only=True,
    )

    class Meta:
        """Configure writable, readable, and protected model fields."""

        model = JobPostingSubmission
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
            "normalization",
        ]

    def validate_pdf(self, pdf):
        """Validate the size, extension, and signature of an uploaded PDF.

        The file must:

        - Be no larger than 5 MB.
        - Have a ``.pdf`` extension.
        - Start with the standard ``%PDF-`` file signature.

        Args:
            pdf (django.core.files.uploadedfile.UploadedFile): File
                uploaded through the API request.

        Returns:
            The validated file with its reading position restored.

        Raises:
            serializers.ValidationError: When the file is too large or
                is not recognized as a PDF.
        """
        if pdf.size > MAX_PDF_SIZE:
            raise serializers.ValidationError(
                "O arquivo PDF não pode exceder 5 MB."
            )

        if not pdf.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Apenas arquivos PDF são aceitos."
            )

        current_position = pdf.tell()
        signature = pdf.read(len(PDF_SIGNATURE))
        pdf.seek(current_position)

        if signature != PDF_SIGNATURE:
            raise serializers.ValidationError(
                "O arquivo enviado não é um PDF válido."
            )

        return pdf

    def validate(self, attrs):
        """Validate the relationship between source, raw text, and PDF.

        Text submissions must contain only ``raw_text``. PDF submissions
        must contain only the ``pdf`` field. Text is cleaned and checked
        against the configured character limits.

        Args:
            attrs (dict): Request data already processed by field
                validators.

        Returns:
            Validated and cleaned request data.

        Raises:
            serializers.ValidationError: When required fields are missing
                or incompatible fields are submitted together.
        """
        source = attrs.get("source")
        raw_text = attrs.get("raw_text")
        pdf = attrs.get("pdf")

        if source == JobPostingSubmission.Source.TEXT:
            if pdf:
                raise serializers.ValidationError({
                    "pdf": (
                        "Não envie um PDF quando source='text'."
                    )
                })

            try:
                attrs["raw_text"] = validate_job_text(raw_text)
            except serializers.ValidationError as exc:
                raise serializers.ValidationError({
                    "raw_text": exc.detail
                }) from exc

        elif source == JobPostingSubmission.Source.PDF:
            if not pdf:
                raise serializers.ValidationError({
                    "pdf": (
                        "Um arquivo PDF é obrigatório quando source='pdf'."
                    )
                })

            if raw_text:
                raise serializers.ValidationError({
                    "raw_text": (
                        "Não envie raw_text quando source='pdf'."
                    )
                })

        else:
            raise serializers.ValidationError({
                "source": (
                    "Source deve ser 'text' ou 'pdf'."
                )
            })

        return attrs
