"""Serializers and input validation for the matching application."""

from rest_framework import serializers

from jobs.models import JobPostingSubmission
from resumes.models import ResumeSubmission

from .models import MatchResult


class MatchResultSerializer(serializers.ModelSerializer):
    """Serialize a match result.

    Read-only because match results are generated internally by the
    application, not submitted directly by the frontend.

    resume_title, job_posting_title, matches, gaps, strengths, and
    weaknesses are all derived from structured_data (resume_title,
    job_posting_title, skills_compativeis, skills_faltantes, pontos_fortes,
    pontos_melhoria) rather than stored as separate columns, since they
    don't need to be queried/filtered on their own. The matching LLM call
    copies resume_title/job_posting_title from its own input, so the match
    result stays a self-contained snapshot even if the underlying resume or
    job posting is renormalized later.
    """

    resume_title = serializers.SerializerMethodField()
    job_posting_title = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    gaps = serializers.SerializerMethodField()
    strengths = serializers.SerializerMethodField()
    weaknesses = serializers.SerializerMethodField()

    class Meta:
        """Configure the match result model representation."""

        model = MatchResult
        fields = [
            "id",
            "resume",
            "resume_title",
            "job_posting",
            "job_posting_title",
            "success",
            "overall_match_score",
            "seniority_compatible",
            "matches",
            "gaps",
            "strengths",
            "weaknesses",
            "structured_data",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_resume_title(self, match_result):
        """Return the candidate's desired role, as copied by the matching LLM call."""
        return (match_result.structured_data or {}).get("resume_title")

    def get_job_posting_title(self, match_result):
        """Return the job title, as copied by the matching LLM call."""
        return (match_result.structured_data or {}).get("job_posting_title")

    def get_matches(self, match_result):
        """Return skills present in both the resume and the job posting."""
        return (match_result.structured_data or {}).get("skills_compativeis")

    def get_gaps(self, match_result):
        """Return skills the job posting requires but the resume lacks."""
        return (match_result.structured_data or {}).get("skills_faltantes")

    def get_strengths(self, match_result):
        """Return the candidate's strong points for this job posting."""
        return (match_result.structured_data or {}).get("pontos_fortes")

    def get_weaknesses(self, match_result):
        """Return the candidate's improvement points for this job posting."""
        return (match_result.structured_data or {}).get("pontos_melhoria")


class MatchRequestSerializer(serializers.Serializer):
    """Validate a request to match one resume against one job posting.

    Both submissions must belong to the requesting user and must already
    have a successful normalization, since the matching prompt is built
    from their structured data.
    """

    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()

    def validate(self, attrs):
        """Resolve resume_id/job_id into owned, normalized submissions."""
        user = self.context["request"].user

        try:
            resume = ResumeSubmission.objects.get(
                pk=attrs["resume_id"], submitted_by=user
            )
        except ResumeSubmission.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"resume_id": "Currículo não encontrado."}
            ) from exc

        try:
            job_posting = JobPostingSubmission.objects.get(
                pk=attrs["job_id"], submitted_by=user
            )
        except JobPostingSubmission.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"job_id": "Vaga não encontrada."}
            ) from exc

        if not getattr(resume, "normalization", None) or not resume.normalization.success:
            raise serializers.ValidationError(
                {"resume_id": "O currículo ainda não foi normalizado com sucesso."}
            )

        if not getattr(job_posting, "normalization", None) or not job_posting.normalization.success:
            raise serializers.ValidationError(
                {"job_id": "A vaga ainda não foi normalizada com sucesso."}
            )

        attrs["resume"] = resume
        attrs["job_posting"] = job_posting
        return attrs
