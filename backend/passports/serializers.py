"""Serializers and input validation for the passports application."""

from rest_framework import serializers

from jobs.models import JobPostingSubmission
from resumes.models import ResumeSubmission

from .models import CandidatePreparationSelfAssessment, StudyTrack, TalentPassport


class StudyTrackSerializer(serializers.ModelSerializer):
    """Serialize a Talent Passport's personalized study track.

    Read-only because the track is generated internally by the passport
    generation service, not submitted directly by the frontend.
    """

    class Meta:
        """Configure the study track model representation."""

        model = StudyTrack
        fields = [
            "success",
            "title",
            "introduction",
            "items",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TalentPassportSerializer(serializers.ModelSerializer):
    """Serialize a Talent Passport and its study track.

    Read-only because a passport is generated internally by the passport
    generation service, not submitted directly by the frontend. The study
    track is included as read-only nested data when it exists.
    """

    study_track = StudyTrackSerializer(read_only=True)

    class Meta:
        """Configure the talent passport model representation."""

        model = TalentPassport
        fields = [
            "id",
            "user",
            "resume",
            "job_posting",
            "success",
            "professional_profile",
            "career_recommendations",
            "dashboard_summary",
            "overall_score",
            "error_message",
            "study_track",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TalentPassportGenerateRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate a request to generate or refresh a Talent Passport.

    Both submissions must belong to the requesting user and must already
    have a successful normalization, since the passport is built from their
    structured data. Deeper upstream checks (match result, assessment
    result) are the responsibility of the generation service.
    """

    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()

    def validate(self, attrs):
        """Resolve resume_id/job_id into owned, normalized submissions."""
        user = self.context["request"].user

        try:
            resume = ResumeSubmission.objects.get(pk=attrs["resume_id"], submitted_by=user)
        except ResumeSubmission.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"resume_id": "Currículo não encontrado."}
            ) from exc

        try:
            job_posting = JobPostingSubmission.objects.get(
                pk=attrs["job_id"], submitted_by=user
            )
        except JobPostingSubmission.DoesNotExist as exc:
            raise serializers.ValidationError({"job_id": "Vaga não encontrada."}) from exc

        if not getattr(resume, "normalization", None) or not resume.normalization.success:
            raise serializers.ValidationError(
                {"resume_id": "O currículo ainda não foi normalizado com sucesso."}
            )

        if (
            not getattr(job_posting, "normalization", None)
            or not job_posting.normalization.success
        ):
            raise serializers.ValidationError(
                {"job_id": "A vaga ainda não foi normalizada com sucesso."}
            )

        attrs["resume"] = resume
        attrs["job_posting"] = job_posting
        return attrs


class CandidatePreparationSelfAssessmentSerializer(serializers.ModelSerializer):
    """Serialize the candidate's waiting-screen preparation self-assessment.

    Read-only: storage-only data the frontend reads back for display, not
    processed or compared against anything on the backend.
    """

    class Meta:
        """Configure the candidate preparation self-assessment model representation."""

        model = CandidatePreparationSelfAssessment
        fields = [
            "id",
            "resume",
            "job_posting",
            "perceived_preparation_percentage",
            "application_threshold_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CandidatePreparationSelfAssessmentQuerySerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate the identifiers used to retrieve a readiness self-assessment."""

    resume_id = serializers.UUIDField(required=True)
    job_id = serializers.UUIDField(required=True)


class CandidatePreparationSelfAssessmentSubmitSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate a request to submit or update the candidate's preparation self-assessment.

    Both submissions must belong to the requesting user.
    """

    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()
    perceived_preparation_percentage = serializers.IntegerField(min_value=0, max_value=100)
    application_threshold_percentage = serializers.IntegerField(min_value=0, max_value=100)

    def validate(self, attrs):
        """Resolve resume_id/job_id into owned submissions."""
        user = self.context["request"].user

        try:
            resume = ResumeSubmission.objects.get(pk=attrs["resume_id"], submitted_by=user)
        except ResumeSubmission.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"resume_id": "Currículo não encontrado."}
            ) from exc

        try:
            job_posting = JobPostingSubmission.objects.get(
                pk=attrs["job_id"], submitted_by=user
            )
        except JobPostingSubmission.DoesNotExist as exc:
            raise serializers.ValidationError({"job_id": "Vaga não encontrada."}) from exc

        attrs["resume"] = resume
        attrs["job_posting"] = job_posting
        return attrs
