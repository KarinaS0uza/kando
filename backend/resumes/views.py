"""Authenticated API views for creating and accessing resumes."""

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ResumeSubmission, ResumeNormalization
from .serializers import ResumeSerializer, validate_resume_text
from .services.resume_llm_normalization import normalize_resume
from .services.pdf_extraction import (
    PdfExtractionError,
    extract_text_from_pdf,
)


class ResumeListCreateView(APIView):
    """List the authenticated user's resumes or create a new resume.

    GET returns only resumes owned by the authenticated user.

    POST accepts either raw text or a PDF. For PDF submissions, the text is
    extracted before the resume is normalized by the LLM. The resume and
    its normalization result are then saved in a single database transaction.

    If the LLM call fails, the resume is still saved and its normalization
    record is created with ``success=False`` and the corresponding error.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all resumes owned by the authenticated user."""
        resumes = ResumeSubmission.objects.filter(
            submitted_by=request.user
        )

        serializer = ResumeSerializer(
            resumes,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Validate, process, normalize, and create a resume.

        Text submissions are sent directly to the normalization service.
        PDF submissions are first converted to text, then checked against
        the same length limits enforced for direct text submissions.

        A PDF extraction error or a length violation produces a 400
        response, while an LLM error is stored in a failed normalization
        record without preventing the creation of the resume.
        """
        serializer = ResumeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        pdf = validated_data.pop("pdf", None)

        if validated_data.get("source") == ResumeSubmission.Source.PDF:
            try:
                extracted_text = extract_text_from_pdf(pdf)
            except PdfExtractionError as exc:
                return Response(
                    {"pdf": [str(exc)]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                validated_data["raw_text"] = validate_resume_text(extracted_text)
            except serializers.ValidationError as exc:
                return Response(
                    {"pdf": exc.detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        validated_data["submitted_by"] = request.user

        normalization_result = normalize_resume(
            validated_data["raw_text"]
        )

        # Content-type gate: when the LLM identifies the text as not a resume
        # (for example a job posting pasted into the resume field), reject with
        # 400 and do not persist, so mismatched documents never enter the
        # database. Only an explicit ``True`` rejects; an absent field or a
        # technical error falls through unchanged.
        if normalization_result.get("entrada_invalida") is True:
            reason = normalization_result.get("motivo_entrada_invalida")
            return Response(
                {"raw_text": [
                    reason or (
                        "O texto enviado não parece ser um currículo. "
                        "Verifique se você não colou uma vaga por engano."
                    )
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            resume = ResumeSubmission.objects.create(
                **validated_data
            )

            if "error" in normalization_result:
                normalization = (
                    ResumeNormalization.objects.create(
                        resume=resume,
                        success=False,
                        error_message=normalization_result["error"],
                    )
                )
            else:
                # Drop the discriminator so it does not leak into the persisted
                # structured data consumed by matching and question generation.
                normalization_result.pop("entrada_invalida", None)
                normalization = (
                    ResumeNormalization.objects.create(
                        resume=resume,
                        success=True,
                        structured_data=normalization_result,
                    )
                )

        resume.normalization = normalization

        output_serializer = ResumeSerializer(resume)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ResumeDetailView(APIView):
    """Retrieve or delete a resume owned by the authenticated user.

    Object queries include the authenticated user so one user cannot access
    another user's resume.

    The delete permission may be restricted to admin users after the current
    development and testing phase.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return a resume belonging to the user, or ``None`` if absent."""
        try:
            return ResumeSubmission.objects.get(
                pk=pk,
                submitted_by=user,
            )
        except ResumeSubmission.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return one resume owned by the authenticated user."""
        resume = self.get_object(pk, request.user)

        if resume is None:
            return Response(
                {"detail": "Currículo não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ResumeSerializer(resume)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete one resume owned by the authenticated user."""
        resume = self.get_object(pk, request.user)

        if resume is None:
            return Response(
                {"detail": "Currículo não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        resume.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
