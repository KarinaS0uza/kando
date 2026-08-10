"""Authenticated API views for requesting and accessing match results."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MatchResult
from .serializers import MatchRequestSerializer, MatchResultSerializer
from .services.matching_llm_analysis import analyze_match


class MatchListCreateView(APIView):
    """List the authenticated user's match results or request a new match.

    GET returns only match results for resumes owned by the authenticated
    user.

    POST accepts a resume_id and a job_id, both of which must belong to the
    authenticated user and already have a successful normalization. Running
    a match for a pair that was already matched overwrites the previous
    result instead of creating a new one.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all match results owned by the authenticated user."""
        matches = MatchResult.objects.filter(resume__submitted_by=request.user)

        serializer = MatchResultSerializer(matches, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Validate the pair, run the LLM analysis, and upsert the result."""
        input_serializer = MatchRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        resume = input_serializer.validated_data["resume"]
        job_posting = input_serializer.validated_data["job_posting"]

        analysis_result = analyze_match(
            resume.normalization.structured_data,
            job_posting.normalization.structured_data,
        )

        if "error" in analysis_result:
            defaults = {
                "success": False,
                "overall_match_score": None,
                "seniority_compatible": None,
                "structured_data": None,
                "error_message": analysis_result["error"],
            }
        else:
            defaults = {
                "success": True,
                "overall_match_score": analysis_result.get("compatibility_score"),
                "seniority_compatible": analysis_result.get("seniority_compatible"),
                "structured_data": analysis_result,
                "error_message": None,
            }

        match_result, created = MatchResult.objects.update_or_create(
            resume=resume,
            job_posting=job_posting,
            defaults=defaults,
        )

        output_serializer = MatchResultSerializer(match_result)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MatchDetailView(APIView):
    """Retrieve or delete a match result owned by the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Return a match result belonging to the user, or ``None`` if absent."""
        try:
            return MatchResult.objects.get(
                pk=pk,
                resume__submitted_by=user,
            )
        except MatchResult.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return one match result owned by the authenticated user."""
        match_result = self.get_object(pk, request.user)

        if match_result is None:
            return Response(
                {"detail": "Compatibilidade não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MatchResultSerializer(match_result)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete one match result owned by the authenticated user."""
        match_result = self.get_object(pk, request.user)

        if match_result is None:
            return Response(
                {"detail": "Compatibilidade não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        match_result.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
