"""Serializers and input validation for the assessments application."""

from rest_framework import serializers

from jobs.models import JobPostingSubmission
from resumes.models import ResumeSubmission

from .models import Assessment, AssessmentResult


class AssessmentResultSerializer(serializers.ModelSerializer):
    """Serialize the graded result of an assessment.

    Read-only because the score and study track are generated internally by
    the LLM grading service, not submitted directly by the frontend.
    """

    pontos_fortes = serializers.SerializerMethodField()

    class Meta:
        """Configure the assessment result representation."""

        model = AssessmentResult
        fields = [
            "success",
            "score",
            "pontos_fortes",
            "answers",
            "study_track",
            "structured_data",
            "error_message",
            "created_at",
        ]
        # pontos_fortes is a SerializerMethodField (already read-only); listing a
        # declared field in read_only_fields raises, so keep it out of this list.
        read_only_fields = [
            "success",
            "score",
            "answers",
            "study_track",
            "structured_data",
            "error_message",
            "created_at",
        ]

    def get_pontos_fortes(self, result):
        """Surface the aggregation strengths at the top level for the dashboard.

        The strengths are computed by ``score_aggregation`` and stored nested
        under ``structured_data['aggregation']['avaliacao']['pontos_fortes']``;
        exposing them directly saves the frontend from traversing the full
        evaluation payload. Returns an empty list when the result has no
        aggregation yet (e.g. a failed grading).
        """
        data = result.structured_data or {}
        aggregation = data.get("aggregation") or {}
        avaliacao = aggregation.get("avaliacao") or {}
        return avaliacao.get("pontos_fortes", [])


class AssessmentSerializer(serializers.ModelSerializer):
    """Serialize an assessment and its generated questions.

    Read-only because assessments are generated internally by the LLM, not
    submitted directly by the frontend. The graded result is included as
    read-only nested data when it exists.

    ``questions`` is derived from ``structured_data`` (the LLM output) rather
    than stored as a separate column, since it does not need to be
    queried/filtered on its own.
    """

    questions = serializers.SerializerMethodField()
    result = AssessmentResultSerializer(read_only=True)

    class Meta:
        """Configure the assessment model representation."""

        model = Assessment
        fields = [
            "id",
            "resume",
            "job_posting",
            "success",
            "questions",
            "structured_data",
            "error_message",
            "result",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_questions(self, assessment):
        """Return all questions flattened from the challenge blocks, in order.

        The LLM output groups questions under ``blocos[].perguntas``; this
        flattens them into a single ordered list for consumers that iterate
        over questions without caring about the block structure.
        """
        structured_data = assessment.structured_data or {}
        questions = []
        for block in structured_data.get("blocos") or []:
            questions.extend(block.get("perguntas") or [])
        return questions


class AssessmentRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate a request to generate an assessment for a resume and a job.

    Both submissions must belong to the requesting user and must already have
    a successful normalization, since the assessment prompt is built from
    their structured data.
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


class AnswerSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate one submitted answer, tied to a generated question by its id."""

    id = serializers.CharField()
    resposta = serializers.CharField(allow_blank=True, trim_whitespace=False)


class AssessmentGradeRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate a request to grade an assessment from the candidate's answers.

    ``answers`` maps to the generated questions by their ``id`` (e.g. "B1Q1").
    Answers for unknown ids are ignored, and questions with no answer are
    graded as empty (score 0) by the evaluation service.
    """

    answers = AnswerSerializer(many=True)

    def validate_answers(self, value):
        """Require at least one answer in the submission."""
        if not value:
            raise serializers.ValidationError("Envie ao menos uma resposta.")
        return value
