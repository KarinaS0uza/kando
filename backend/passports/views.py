"""Authenticated API views for generating and accessing Talent Passports."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CandidatePreparationSelfAssessment, TalentPassport
from .serializers import (
    CandidatePreparationSelfAssessmentSerializer,
    CandidatePreparationSelfAssessmentSubmitSerializer,
    TalentPassportGenerateRequestSerializer,
    TalentPassportSerializer,
)
from .services.passport_generation import PassportGenerationError, generate_talent_passport


class TalentPassportListCreateView(APIView):
    """List the authenticated user's Talent Passports or generate a new one.

    GET returns only passports owned by the authenticated user.

    POST accepts a resume_id and a job_id, both of which must belong to the
    authenticated user and already have a successful normalization, plus a
    successful match result and assessment result for that pair. Generating
    a passport for a pair that already has one refreshes it in place instead
    of creating a new row.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all Talent Passports owned by the authenticated user."""
        passports = TalentPassport.objects.filter(user=request.user)

        serializer = TalentPassportSerializer(passports, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Validate the request and run the generation workflow."""
        input_serializer = TalentPassportGenerateRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        resume = input_serializer.validated_data["resume"]
        job_posting = input_serializer.validated_data["job_posting"]

        try:
            passport, created = generate_talent_passport(request.user, resume, job_posting)
        except PassportGenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = TalentPassportSerializer(passport)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TalentPassportDetailView(APIView):
    """Retrieve a Talent Passport owned by the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return a Talent Passport belonging to the user, or ``None`` if absent."""
        try:
            return TalentPassport.objects.get(pk=pk, user=user)
        except TalentPassport.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return one Talent Passport owned by the authenticated user."""
        passport = self.get_object(pk, request.user)

        if passport is None:
            return Response(
                {"detail": "Talent Passport não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TalentPassportSerializer(passport)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CandidatePreparationSelfAssessmentView(APIView):
    """Submit, update, or retrieve the authenticated user's preparation self-assessment.

    Storage only: values are saved so the frontend can read them back for
    display, with no comparison or business logic applied to them here.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the self-assessment for one owned (resume, job_posting) pair."""
        try:
            self_assessment = CandidatePreparationSelfAssessment.objects.filter(
                user=request.user,
                resume_id=request.query_params.get("resume_id"),
                job_posting_id=request.query_params.get("job_id"),
            ).first()
        except (ValueError, DjangoValidationError):
            return Response(
                {"detail": "resume_id e job_id devem ser UUIDs válidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self_assessment is None:
            return Response(
                {"detail": "As respostas ainda não foram enviadas para esta candidatura."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CandidatePreparationSelfAssessmentSerializer(self_assessment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Validate the answers and upsert one row per (user, resume, job posting)."""
        input_serializer = CandidatePreparationSelfAssessmentSubmitSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        self_assessment, created = CandidatePreparationSelfAssessment.objects.update_or_create(
            user=request.user,
            resume=data["resume"],
            job_posting=data["job_posting"],
            defaults={
                "perceived_preparation_percentage": data["perceived_preparation_percentage"],
                "application_threshold_percentage": data["application_threshold_percentage"],
            },
        )

        output_serializer = CandidatePreparationSelfAssessmentSerializer(self_assessment)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
