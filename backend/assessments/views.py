"""Authenticated API views for generating and accessing assessments."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assessment, AssessmentResult
from .serializers import (
    AssessmentGradeRequestSerializer,
    AssessmentRequestSerializer,
    AssessmentSerializer,
)
from .services.question_generation import generate_assessment
from .services.score_aggregation import grade_assessment


class AssessmentListCreateView(APIView):
    """List the authenticated user's assessments or generate a new one.

    GET returns only assessments for resumes owned by the authenticated user.

    POST accepts a resume_id and a job_id, both of which must belong to the
    authenticated user and already have a successful normalization. Generating
    an assessment for a pair that already has one overwrites the previous
    questions instead of creating a new row.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all assessments owned by the authenticated user."""
        assessments = Assessment.objects.filter(resume__submitted_by=request.user)

        serializer = AssessmentSerializer(assessments, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Validate the request, run the LLM generation, and upsert the assessment."""
        input_serializer = AssessmentRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        resume = input_serializer.validated_data["resume"]
        job_posting = input_serializer.validated_data["job_posting"]

        generation_result = generate_assessment(
            resume.normalization.structured_data,
            job_posting.normalization.structured_data,
        )

        if "error" in generation_result:
            defaults = {
                "success": False,
                "structured_data": None,
                "error_message": generation_result["error"],
            }
        else:
            defaults = {
                "success": True,
                "structured_data": generation_result,
                "error_message": None,
            }

        assessment, created = Assessment.objects.update_or_create(
            resume=resume,
            job_posting=job_posting,
            defaults=defaults,
        )

        output_serializer = AssessmentSerializer(assessment)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AssessmentDetailView(APIView):
    """Retrieve or delete an assessment owned by the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return an assessment belonging to the user, or ``None`` if absent."""
        try:
            return Assessment.objects.get(
                pk=pk,
                resume__submitted_by=user,
            )
        except Assessment.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return one assessment owned by the authenticated user."""
        assessment = self.get_object(pk, request.user)

        if assessment is None:
            return Response(
                {"detail": "Avaliação não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AssessmentSerializer(assessment)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete one assessment owned by the authenticated user."""
        assessment = self.get_object(pk, request.user)

        if assessment is None:
            return Response(
                {"detail": "Avaliação não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        assessment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class AssessmentResultCreateView(APIView):
    """Grade an assessment from the candidate's answers and store the result.

    POST accepts the answers keyed by question id. Each generated question is
    evaluated by the LLM (empty answers score 0 without a call), the per-question
    scores are averaged deterministically, and the outcome is upserted as the
    assessment's one-to-one result. Re-submitting overwrites the previous
    result instead of creating a new row.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Validate answers, run the LLM evaluation, aggregate, and upsert the result."""
        assessment = (
            Assessment.objects.filter(pk=pk, resume__submitted_by=request.user)
            .select_related("resume__normalization")
            .first()
        )

        if assessment is None:
            return Response(
                {"detail": "Avaliação não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not assessment.success or not assessment.structured_data:
            return Response(
                {"detail": "A avaliação ainda não foi gerada com sucesso."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        input_serializer = AssessmentGradeRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        submitted_answers = input_serializer.validated_data["answers"]

        defaults = grade_assessment(assessment, submitted_answers)

        created = AssessmentResult.objects.update_or_create(
            assessment=assessment,
            defaults=defaults,
        )[1]

        output_serializer = AssessmentSerializer(assessment)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
