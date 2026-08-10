"""Authenticated API views for creating and accessing job postings."""

# Shares the submission-preprocessing flow (serializer validation, PDF
# extraction, text validation) with resumes.views by design; suppress the
# cross-file duplicate-code report until that flow is extracted.
# pylint: disable=duplicate-code

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobPostingSubmission, JobPostingNormalization
from .serializers import JobPostingSerializer, validate_job_text
from .services.job_llm_normalization import normalize_job_posting
from .services.pdf_extraction import (
    PdfExtractionError,
    extract_text_from_pdf,
)


class JobPostingListCreateView(APIView):
    """List the authenticated user's postings or create a new posting.

    GET returns only job postings owned by the authenticated user.

    POST accepts either raw text or a PDF. For PDF submissions, the text is
    extracted before the posting is normalized by the LLM. The posting and
    its normalization result are then saved in a single database transaction.

    If the LLM call fails, the posting is still saved and its normalization
    record is created with ``success=False`` and the corresponding error.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all job postings owned by the authenticated user."""
        job_postings = JobPostingSubmission.objects.filter(
            submitted_by=request.user
        )

        serializer = JobPostingSerializer(
            job_postings,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Validate, process, normalize, and create a job posting.

        Text submissions are sent directly to the normalization service.
        PDF submissions are first converted to text, then checked against
        the same length limits enforced for direct text submissions.

        A PDF extraction error or a length violation produces a 400
        response, while an LLM error is stored in a failed normalization
        record without preventing the creation of the job posting.
        """
        serializer = JobPostingSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        pdf = validated_data.pop("pdf", None)

        if validated_data.get("source") == JobPostingSubmission.Source.PDF:
            try:
                extracted_text = extract_text_from_pdf(pdf)
            except PdfExtractionError as exc:
                return Response(
                    {"pdf": [str(exc)]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                validated_data["raw_text"] = validate_job_text(extracted_text)
            except serializers.ValidationError as exc:
                return Response(
                    {"pdf": exc.detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        validated_data["submitted_by"] = request.user

        normalization_result = normalize_job_posting(
            validated_data["raw_text"]
        )

        # Content-type gate: when the LLM identifies the text as not a job
        # posting (for example a resume pasted into the job field), reject with
        # 400 and do not persist, so mismatched documents never enter the
        # database. Only an explicit ``False`` rejects; an absent field (prompt
        # not yet updated) or a technical error falls through unchanged.
        if normalization_result.get("is_job_posting") is False:
            return Response(
                {"raw_text": [
                    "O texto enviado não parece ser uma vaga. "
                    "Verifique se você não colou um currículo por engano."
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            job_posting = JobPostingSubmission.objects.create(
                **validated_data
            )

            if "error" in normalization_result:
                normalization = (
                    JobPostingNormalization.objects.create(
                        job_posting=job_posting,
                        success=False,
                        error_message=normalization_result["error"],
                    )
                )
            else:
                # Drop the discriminator so it does not leak into the persisted
                # structured data consumed by matching and question generation.
                normalization_result.pop("is_job_posting", None)
                normalization = (
                    JobPostingNormalization.objects.create(
                        job_posting=job_posting,
                        success=True,
                        structured_data=normalization_result,
                    )
                )

        job_posting.normalization = normalization

        output_serializer = JobPostingSerializer(job_posting)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class JobPostingDetailView(APIView):
    """Retrieve or delete a posting owned by the authenticated user.

    Object queries include the authenticated user so one user cannot access
    another user's posting.

    The delete permission may be restricted to admin users after the current
    development and testing phase.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return a posting belonging to the user, or ``None`` if absent."""
        try:
            return JobPostingSubmission.objects.get(
                pk=pk,
                submitted_by=user,
            )
        except JobPostingSubmission.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return one posting owned by the authenticated user."""
        job_posting = self.get_object(pk, request.user)

        if job_posting is None:
            return Response(
                {"detail": "Vaga não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = JobPostingSerializer(job_posting)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete one posting owned by the authenticated user."""
        job_posting = self.get_object(pk, request.user)

        if job_posting is None:
            return Response(
                {"detail": "Vaga não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        job_posting.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
