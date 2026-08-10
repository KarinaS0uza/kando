"""Tests for the passports app: models, services, serializers, and endpoints."""

import uuid
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse

from resumes.models import ResumeSubmission

from .models import CandidatePreparationSelfAssessment, StudyTrack, TalentPassport
from .serializers import (
    CandidatePreparationSelfAssessmentSubmitSerializer,
    TalentPassportGenerateRequestSerializer,
)
from .services import dashboard, profile_recommendations, study_track
from .services.passport_generation import (
    PassportGenerationError,
    generate_talent_passport,
    resolve_role_and_seniority,
    resolve_upstream_records,
)

PROFILE_STUB = {
    "talent_passport": {
        "professional_summary": "Resumo profissional de teste.",
        "overall_level": "pleno",
        "competencies": [{"skill": "React", "evidence": ["evidência de teste"]}],
        "strengths": ["React"],
        "development_areas": ["TypeScript"],
        "suggested_roles": [
            {
                "cargo": "Frontend Developer",
                "match_percentage": 80,
                "rationale": "Boa aderência.",
                "missing_skills": [],
            }
        ],
        "suggested_resources": [
            {"related_skill": "TypeScript", "tipo": "curso", "sugestao": "Curso de TS"}
        ],
    },
    "metadata": {"confianca_geral": 0.8, "campos_nao_encontrados": []},
}

STUDY_NARRATIVE_STUB = {
    "study_track_title": "Trilha para Frontend Developer",
    "introduction": "Introdução de teste.",
    "items": [{"position": 1, "skill": "TypeScript", "motivation": "Importante para a vaga."}],
}


def mock_llm(monkeypatch, profile_result=None, narrative_result=None):
    """Patch both LLM call sites used by passport generation."""
    monkeypatch.setattr(
        "passports.services.profile_recommendations.run_prompt_safe",
        lambda *args, **kwargs: profile_result or PROFILE_STUB,
    )
    monkeypatch.setattr(
        "passports.services.study_track.run_prompt_safe",
        lambda *args, **kwargs: narrative_result or STUDY_NARRATIVE_STUB,
    )


def test_resolve_role_uses_canonical_job_title():
    """The study track uses the canonical normalized job-title field."""
    job_normalization = SimpleNamespace(structured_data={"job_title": "Data Engineer"})
    resume_normalization = SimpleNamespace(structured_data={"calculated_seniority": "pleno"})

    role, seniority = resolve_role_and_seniority(job_normalization, resume_normalization)

    assert role == "Data Engineer"
    assert seniority == "pleno"


def test_resolve_role_supports_legacy_nested_job_title():
    """Existing normalized rows using vaga.titulo remain readable."""
    job_normalization = SimpleNamespace(structured_data={"vaga": {"titulo": "Backend Developer"}})
    resume_normalization = SimpleNamespace(structured_data={})

    role, _ = resolve_role_and_seniority(job_normalization, resume_normalization)

    assert role == "Backend Developer"


def test_resolve_role_falls_back_when_no_title_field_present():
    """A normalized job with none of the known title fields still yields a usable role."""
    job_normalization = SimpleNamespace(structured_data={})
    resume_normalization = SimpleNamespace(structured_data={})

    role, _ = resolve_role_and_seniority(job_normalization, resume_normalization)

    assert role == "a vaga"


@pytest.fixture(name="full_upstream")
def full_upstream_fixture(
    user,
    normalized_resume_factory,
    normalized_job_posting_factory,
    match_result_factory,
    graded_assessment_factory,
):
    """Return fully prepared upstream records for passport generation."""
    resume = normalized_resume_factory(
        user,
        technical_skills=[{"nome": "React", "categoria": "framework", "confidence_level": 0.9}],
        candidate={"desired_job_title": "Frontend Developer"},
    )
    job = normalized_job_posting_factory(user, job_title="Frontend Developer")
    match_result = match_result_factory(resume, job)
    assessment_result = graded_assessment_factory(resume, job)
    return SimpleNamespace(
        resume=resume, job=job, match_result=match_result, assessment_result=assessment_result
    )


@pytest.fixture(name="other_passport")
def other_passport_fixture(
    other_user,
    normalized_resume_factory,
    normalized_job_posting_factory,
    match_result_factory,
    graded_assessment_factory,
):
    """Create a Talent Passport owned by the secondary test user."""
    resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(other_user)
    return TalentPassport.objects.create(
        user=other_user,
        resume=resume,
        job_posting=job,
        match_result=match_result_factory(resume, job),
        assessment_result=graded_assessment_factory(resume, job),
        success=True,
    )


# --- Model tests ---------------------------------------------------------


@pytest.mark.django_db
def test_talent_passport_duplicate_resume_job_pair_rejected(user, full_upstream):
    """A second TalentPassport for the same (resume, job_posting) pair is rejected."""
    TalentPassport.objects.create(
        user=user,
        resume=full_upstream.resume,
        job_posting=full_upstream.job,
        match_result=full_upstream.match_result,
        assessment_result=full_upstream.assessment_result,
        success=True,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            TalentPassport.objects.create(
                user=user,
                resume=full_upstream.resume,
                job_posting=full_upstream.job,
                match_result=full_upstream.match_result,
                assessment_result=full_upstream.assessment_result,
                success=True,
            )


@pytest.mark.django_db
def test_study_track_one_to_one_with_talent_passport(user, full_upstream):
    """A second StudyTrack for the same TalentPassport is rejected."""
    passport = TalentPassport.objects.create(
        user=user,
        resume=full_upstream.resume,
        job_posting=full_upstream.job,
        match_result=full_upstream.match_result,
        assessment_result=full_upstream.assessment_result,
        success=True,
    )
    StudyTrack.objects.create(talent_passport=passport, success=True)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            StudyTrack.objects.create(talent_passport=passport, success=True)


@pytest.mark.django_db
def test_waiting_screen_readiness_duplicate_rejected(
    user, normalized_resume_factory, normalized_job_posting_factory
):
    """The same user cannot submit readiness twice for the same flow."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    CandidatePreparationSelfAssessment.objects.create(
        user=user,
        resume=resume,
        job_posting=job,
        perceived_preparation_percentage=50,
        application_threshold_percentage=50,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            CandidatePreparationSelfAssessment.objects.create(
                user=user,
                resume=resume,
                job_posting=job,
                perceived_preparation_percentage=60,
                application_threshold_percentage=60,
            )


@pytest.mark.django_db
def test_waiting_screen_readiness_value_out_of_range_fails_validation(
    user, normalized_resume_factory, normalized_job_posting_factory
):
    """A percentage outside 0-100 fails model validation."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    readiness = CandidatePreparationSelfAssessment(
        user=user,
        resume=resume,
        job_posting=job,
        perceived_preparation_percentage=150,
        application_threshold_percentage=50,
    )

    with pytest.raises(ValidationError):
        readiness.full_clean()


# --- Service tests: dashboard ---------------------------------------------


def test_calculate_final_score_weights_matching_and_assessment():
    """The final score is 40% matching + 60% assessment, rounded."""
    assert dashboard.calculate_final_score(80, 60) == 68


def test_aggregate_by_topic_ignores_failed_evaluations():
    """A failed evaluation does not contribute to its topic's mean."""
    structured_data = {
        "blocks": [
            {"topic": "React", "questions": [{"id": "B1Q1"}, {"id": "B1Q2"}]},
        ]
    }
    evaluations = [
        {"id": "B1Q1", "evaluation": {"score": 80}},
        {"id": "B1Q2", "error": "falhou"},
    ]

    assert dashboard.aggregate_by_topic(structured_data, evaluations) == {"React": 80}


def test_extract_performance_by_skill_reuses_consolidated_skills():
    """Skill scores are read directly from the already-consolidated aggregation."""
    structured_data = {
        "aggregation": {
            "evaluation": {
                "skills": [
                    {"name": "React", "score": 90},
                    {"name": "Node.js", "score": 40},
                ]
            }
        }
    }

    assert dashboard.extract_performance_by_skill(structured_data) == {"React": 90, "Node.js": 40}


def test_generate_summary_feedback_no_data():
    """An empty performance map returns the 'not enough data' message."""
    assert "dados suficientes" in dashboard.generate_summary_feedback({}).lower()


def test_generate_summary_feedback_best_and_worst_differ():
    """Two different areas produce a best-vs-worst sentence."""
    feedback = dashboard.generate_summary_feedback({"React": 90, "Git": 20})

    assert "React" in feedback
    assert "Git" in feedback


@pytest.mark.django_db
def test_build_dashboard_summary_computes_expected_shape(full_upstream):
    """The dashboard summary combines match/assessment data deterministically."""
    assessment_result = full_upstream.assessment_result

    summary = dashboard.build_dashboard_summary(
        assessment_result.assessment, assessment_result, full_upstream.match_result
    )

    assert summary["overall_score"] == dashboard.calculate_final_score(80, 60)
    assert summary["job_compatibility"] == 80
    assert summary["technical_performance"] == 60
    assert summary["best_area"] == "React"
    assert summary["performance_by_skill"] == {"React": 72, "Node.js": 40}


# --- Service tests: profile_recommendations --------------------------------


@pytest.mark.parametrize(
    "confidence,expected",
    [(0.2, "beginner"), (0.5, "intermediate"), (0.7, "advanced"), (0.9, "expert")],
)
def test_classify_proficiency_bands(confidence, expected):
    """Each confidence band maps to its proficiency label."""
    assert profile_recommendations.classify_proficiency(confidence) == expected


def test_attach_proficiency_levels_exact_match():
    """An exact skill-name match uses the resume's own confidence level."""
    profile_result = {"talent_passport": {"competencies": [{"skill": "React"}]}}
    resume_data = {"technical_skills": [{"name": "React", "confidence_level": 0.9}]}

    profile_recommendations.attach_proficiency_levels(profile_result, resume_data)

    competency = profile_result["talent_passport"]["competencies"][0]
    assert competency["confidence_match"] == "exact"
    assert competency["proficiency_level"] == "expert"


def test_attach_proficiency_levels_fallback_when_no_match():
    """An unmatched skill name falls back to the default confidence."""
    profile_result = {"talent_passport": {"competencies": [{"skill": "Rust"}]}}
    resume_data = {"technical_skills": [{"name": "React", "confidence_level": 0.9}]}

    profile_recommendations.attach_proficiency_levels(profile_result, resume_data)

    competency = profile_result["talent_passport"]["competencies"][0]
    assert competency["confidence_match"] == "unmatched_fallback"
    assert competency["proficiency_level"] == "intermediate"


def test_generate_professional_profile_returns_error_dict_on_llm_failure(monkeypatch):
    """An LLM failure degrades to an {"error", "retryable"} dict, not an exception."""
    monkeypatch.setattr(
        "passports.services.profile_recommendations.run_prompt_safe",
        lambda *args, **kwargs: {"error": "Falha ao chamar o LLM: boom", "retryable": True},
    )

    result = profile_recommendations.generate_professional_profile({}, {}, {})

    assert result == {"error": "Falha ao chamar o LLM: boom", "retryable": True}


def test_generate_professional_profile_degrades_on_malformed_llm_shape(monkeypatch):
    """A well-formed but wrongly-shaped LLM response degrades instead of crashing."""
    monkeypatch.setattr(
        "passports.services.profile_recommendations.run_prompt_safe",
        lambda *args, **kwargs: {"talent_passport": {"competencies": ["React"]}},
    )

    result = profile_recommendations.generate_professional_profile({}, {}, {})

    assert result["error"]
    assert result["retryable"] is True


def test_generate_professional_profile_success_attaches_proficiency(monkeypatch):
    """A successful call returns the LLM output with proficiency levels attached."""
    monkeypatch.setattr(
        "passports.services.profile_recommendations.run_prompt_safe",
        lambda *args, **kwargs: PROFILE_STUB,
    )
    resume_data = {"technical_skills": [{"name": "React", "confidence_level": 0.9}]}

    result = profile_recommendations.generate_professional_profile(resume_data, {}, {})

    competency = result["talent_passport"]["competencies"][0]
    assert competency["proficiency_level"] == "expert"


# --- Service tests: study_track --------------------------------------------


def test_calculate_skill_priority_scoring():
    """Missing skills, development areas, and low performance all add priority."""
    ordered = study_track.calculate_skill_priority(
        missing_skills=["A", "B"],
        development_areas=["B", "C"],
        performance_by_skill={"A": 30},
    )

    assert ordered == ["A", "B", "C"]


def test_build_base_study_track_pairs_resources_by_skill():
    """A skill with a matching resource gets it; one without gets None."""
    track = study_track.build_base_study_track(
        ["TypeScript", "Docker"],
        [{"related_skill": "TypeScript", "type": "course", "suggestion": "TypeScript course"}],
    )

    assert track[0] == {
        "position": 1,
        "skill": "TypeScript",
        "resource_type": "course",
        "resource_suggestion": "TypeScript course",
    }
    assert track[1]["resource_type"] is None


def test_generate_study_track_returns_empty_when_no_gaps():
    """No missing skills or development areas produces an empty, successful track."""
    result = study_track.generate_study_track(
        study_track.StudyTrackInput(
            role="Dev",
            seniority="mid_level",
            missing_skills=[],
            development_areas=[],
            suggested_resources=[],
        )
    )

    assert result["success"] is True
    assert not result["items"]


def test_generate_study_track_falls_back_when_narrative_fails(monkeypatch):
    """A failed narrative call still returns a usable, ordered track."""
    monkeypatch.setattr(
        "passports.services.study_track.run_prompt_safe",
        lambda *args, **kwargs: {"error": "boom", "retryable": True},
    )

    result = study_track.generate_study_track(
        study_track.StudyTrackInput(
            role="Dev",
            seniority="mid_level",
            missing_skills=["TypeScript"],
            development_areas=[],
            suggested_resources=[
                {
                    "related_skill": "TypeScript",
                    "type": "course",
                    "suggestion": "x",
                }
            ],
        )
    )

    assert result["success"] is True
    assert result["narrative_error"] == "boom"
    assert result["items"][0]["skill"] == "TypeScript"
    assert result["items"][0]["motivation"] == ""


def test_generate_study_track_falls_back_when_narrative_shape_is_malformed(monkeypatch):
    """A well-formed but wrongly-shaped narrative degrades like a failed call, not a crash."""
    monkeypatch.setattr(
        "passports.services.study_track.run_prompt_safe",
        lambda *args, **kwargs: {"items": ["not", "a", "dict"]},
    )

    result = study_track.generate_study_track(
        study_track.StudyTrackInput(
            role="Dev",
            seniority="mid_level",
            missing_skills=["TypeScript"],
            development_areas=[],
            suggested_resources=[
                {
                    "related_skill": "TypeScript",
                    "type": "course",
                    "suggestion": "x",
                }
            ],
        )
    )

    assert result["success"] is True
    assert result["narrative_error"]
    assert result["items"][0]["skill"] == "TypeScript"
    assert result["items"][0]["motivation"] == ""


# --- Service tests: passport_generation (orchestration) --------------------


@pytest.mark.django_db
def test_resolve_upstream_records_rejects_ownership_mismatch(other_user, full_upstream):
    """A resume/job pair not owned by the given user is rejected."""
    with pytest.raises(PassportGenerationError):
        resolve_upstream_records(other_user, full_upstream.resume, full_upstream.job)


@pytest.mark.django_db
def test_resolve_upstream_records_rejects_unnormalized_resume(user, normalized_job_posting_factory):
    """A resume without a successful normalization is rejected."""
    resume = ResumeSubmission.objects.create(submitted_by=user, source="text", raw_text="y" * 200)
    job = normalized_job_posting_factory(user)

    with pytest.raises(PassportGenerationError):
        resolve_upstream_records(user, resume, job)


@pytest.mark.django_db
def test_resolve_upstream_records_rejects_missing_match(
    user, normalized_resume_factory, normalized_job_posting_factory
):
    """A pair with no match result is rejected."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)

    with pytest.raises(PassportGenerationError):
        resolve_upstream_records(user, resume, job)


@pytest.mark.django_db
def test_resolve_upstream_records_rejects_ungraded_assessment(
    user, normalized_resume_factory, normalized_job_posting_factory, match_result_factory
):
    """A pair with no graded assessment result is rejected."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    match_result_factory(resume, job)

    with pytest.raises(PassportGenerationError):
        resolve_upstream_records(user, resume, job)


@pytest.mark.django_db
def test_generate_talent_passport_success_creates_passport_and_study_track(
    user, full_upstream, monkeypatch
):
    """A full generation run creates one TalentPassport and one StudyTrack, both successful."""
    mock_llm(monkeypatch)

    passport, created = generate_talent_passport(user, full_upstream.resume, full_upstream.job)

    assert created is True
    assert passport.success is True
    assert passport.overall_score == dashboard.calculate_final_score(80, 60)
    assert passport.professional_profile["overall_level"] == "mid_level"
    assert StudyTrack.objects.get(talent_passport=passport).success is True


@pytest.mark.django_db
def test_generate_talent_passport_tolerates_null_match_structured_data(
    user, full_upstream, monkeypatch
):
    """A successful MatchResult with a null structured_data does not crash generation."""
    mock_llm(monkeypatch)
    full_upstream.match_result.structured_data = None
    full_upstream.match_result.save()

    passport, _ = generate_talent_passport(user, full_upstream.resume, full_upstream.job)

    assert passport.success is True


@pytest.mark.django_db
def test_generate_talent_passport_is_idempotent(user, full_upstream, monkeypatch):
    """Regenerating for the same pair updates the existing row instead of duplicating it."""
    mock_llm(monkeypatch)
    resume, job = full_upstream.resume, full_upstream.job

    first_passport, first_created = generate_talent_passport(user, resume, job)
    second_passport, second_created = generate_talent_passport(user, resume, job)

    assert first_created is True
    assert second_created is False
    assert first_passport.id == second_passport.id
    assert TalentPassport.objects.filter(resume=resume, job_posting=job).count() == 1
    assert StudyTrack.objects.filter(talent_passport=first_passport).count() == 1


@pytest.mark.django_db
def test_generate_talent_passport_profile_failure_still_saves_dashboard(
    user, full_upstream, monkeypatch
):
    """A profile failure is saved without losing the deterministic dashboard."""
    mock_llm(monkeypatch, profile_result={"error": "boom", "retryable": True})

    passport = generate_talent_passport(user, full_upstream.resume, full_upstream.job)[0]

    assert passport.success is False
    assert passport.error_message == "boom"
    assert passport.professional_profile is None
    assert passport.dashboard_summary is not None
    assert passport.overall_score == dashboard.calculate_final_score(80, 60)


@pytest.mark.django_db
def test_generate_talent_passport_rolls_back_on_save_failure(user, full_upstream, monkeypatch):
    """If saving the StudyTrack fails, the TalentPassport write is rolled back too."""
    mock_llm(monkeypatch)
    resume, job = full_upstream.resume, full_upstream.job

    def boom(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "passports.services.passport_generation.StudyTrack.objects.update_or_create", boom
    )

    with pytest.raises(RuntimeError):
        generate_talent_passport(user, resume, job)

    assert not TalentPassport.objects.filter(resume=resume, job_posting=job).exists()


# --- Serializer tests -------------------------------------------------------


class FakeRequest:  # pylint: disable=too-few-public-methods
    """Minimal stand-in for a DRF request, exposing only .user."""

    def __init__(self, user):
        self.user = user


@pytest.mark.django_db
def test_generate_request_serializer_rejects_unowned_resume(
    user,
    other_user,
    normalized_resume_factory,
    normalized_job_posting_factory,
):
    """A resume_id owned by another user fails validation."""
    other_resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(user)
    serializer = TalentPassportGenerateRequestSerializer(
        data={"resume_id": str(other_resume.id), "job_id": str(job.id)},
        context={"request": FakeRequest(user)},
    )

    assert not serializer.is_valid()
    assert "resume_id" in serializer.errors


@pytest.mark.django_db
def test_waiting_readiness_submit_serializer_rejects_unowned_resume(
    user, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """A resume_id owned by another user fails validation."""
    other_resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(user)
    serializer = CandidatePreparationSelfAssessmentSubmitSerializer(
        data={
            "resume_id": str(other_resume.id),
            "job_id": str(job.id),
            "perceived_preparation_percentage": 50,
            "application_threshold_percentage": 50,
        },
        context={"request": FakeRequest(user)},
    )

    assert not serializer.is_valid()
    assert "resume_id" in serializer.errors


def test_waiting_readiness_submit_serializer_rejects_out_of_range_value():
    """A percentage above 100 fails serializer validation."""
    serializer = CandidatePreparationSelfAssessmentSubmitSerializer(
        data={
            "resume_id": str(uuid.uuid4()),
            "job_id": str(uuid.uuid4()),
            "perceived_preparation_percentage": 150,
            "application_threshold_percentage": 50,
        },
        context={"request": FakeRequest(None)},
    )

    assert not serializer.is_valid()
    assert "perceived_preparation_percentage" in serializer.errors


# --- Endpoint tests ----------------------------------------------------------

PASSPORT_LIST_URL = reverse("passports:passport-list-create")
READINESS_URL = reverse("passports:waiting-readiness")


def passport_detail_url(pk):
    """Return the detail URL for a given Talent Passport id."""
    return reverse("passports:passport-detail", kwargs={"pk": pk})


@pytest.mark.django_db
def test_passport_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(PASSPORT_LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_passport_list_returns_only_owned_passports(
    auth_client,
    full_upstream,
    other_passport,
):
    """Passports belonging to another user are excluded from the list."""
    TalentPassport.objects.create(
        user=full_upstream.resume.submitted_by,
        resume=full_upstream.resume,
        job_posting=full_upstream.job,
        match_result=full_upstream.match_result,
        assessment_result=full_upstream.assessment_result,
        success=True,
    )

    assert other_passport.user_id != full_upstream.resume.submitted_by_id

    response = auth_client.get(PASSPORT_LIST_URL)

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_passport_create_rejects_unknown_resume_id(
    auth_client, user, normalized_job_posting_factory
):
    """A resume_id that does not belong to the caller returns 400."""
    job = normalized_job_posting_factory(user)

    response = auth_client.post(
        PASSPORT_LIST_URL, {"resume_id": str(uuid.uuid4()), "job_id": str(job.id)}, format="json"
    )

    assert response.status_code == 400
    assert "resume_id" in response.data


@pytest.mark.django_db
def test_passport_create_returns_400_when_match_missing(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """A pair without a successful match result cannot generate a passport."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)

    response = auth_client.post(
        PASSPORT_LIST_URL, {"resume_id": str(resume.id), "job_id": str(job.id)}, format="json"
    )

    assert response.status_code == 400
    assert "detail" in response.data


@pytest.mark.django_db
def test_passport_create_succeeds_and_rerun_upserts(auth_client, user, full_upstream, monkeypatch):
    """A successful generation is created once, then updated in place on rerun."""
    mock_llm(monkeypatch)
    resume, job = full_upstream.resume, full_upstream.job
    payload = {"resume_id": str(resume.id), "job_id": str(job.id)}

    first_response = auth_client.post(PASSPORT_LIST_URL, payload, format="json")
    assert first_response.status_code == 201
    assert first_response.data["success"] is True

    second_response = auth_client.post(PASSPORT_LIST_URL, payload, format="json")
    assert second_response.status_code == 200
    assert TalentPassport.objects.filter(resume=resume, job_posting=job, user=user).count() == 1


@pytest.mark.django_db
def test_passport_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(passport_detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_passport_detail_returns_404_for_other_users_passport(
    auth_client, other_user, full_upstream
):
    """A passport owned by another user is not visible."""
    passport = TalentPassport.objects.create(
        user=other_user,
        resume=full_upstream.resume,
        job_posting=full_upstream.job,
        match_result=full_upstream.match_result,
        assessment_result=full_upstream.assessment_result,
        success=True,
    )

    response = auth_client.get(passport_detail_url(passport.id))

    assert response.status_code == 404


@pytest.mark.django_db
def test_waiting_readiness_submit_creates_and_updates(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """Submitting again for the same flow updates the existing row instead of duplicating it."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    payload = {
        "resume_id": str(resume.id),
        "job_id": str(job.id),
        "perceived_preparation_percentage": 40,
        "application_threshold_percentage": 70,
    }

    first_response = auth_client.post(READINESS_URL, payload, format="json")
    assert first_response.status_code == 201
    assert first_response.data["perceived_preparation_percentage"] == 40

    payload["perceived_preparation_percentage"] = 90
    second_response = auth_client.post(READINESS_URL, payload, format="json")

    assert second_response.status_code == 200
    assert second_response.data["perceived_preparation_percentage"] == 90
    assert (
        CandidatePreparationSelfAssessment.objects.filter(
            user=user, resume=resume, job_posting=job
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_waiting_readiness_submit_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.post(
        READINESS_URL,
        {
            "resume_id": str(uuid.uuid4()),
            "job_id": str(uuid.uuid4()),
            "perceived_preparation_percentage": 50,
            "application_threshold_percentage": 50,
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_waiting_readiness_submit_rejects_other_users_resume(
    auth_client, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """A resume_id owned by another user is rejected."""
    resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(other_user)

    response = auth_client.post(
        READINESS_URL,
        {
            "resume_id": str(resume.id),
            "job_id": str(job.id),
            "perceived_preparation_percentage": 50,
            "application_threshold_percentage": 50,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "resume_id" in response.data


@pytest.mark.django_db
def test_waiting_readiness_get_returns_saved_values(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """A GET after submission returns the saved readiness values for that flow."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    CandidatePreparationSelfAssessment.objects.create(
        user=user,
        resume=resume,
        job_posting=job,
        perceived_preparation_percentage=35,
        application_threshold_percentage=80,
    )

    response = auth_client.get(READINESS_URL, {"resume_id": str(resume.id), "job_id": str(job.id)})

    assert response.status_code == 200
    assert response.data["perceived_preparation_percentage"] == 35
    assert response.data["application_threshold_percentage"] == 80


@pytest.mark.django_db
def test_waiting_readiness_get_returns_404_when_not_submitted(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """A GET before any submission returns 404."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)

    response = auth_client.get(READINESS_URL, {"resume_id": str(resume.id), "job_id": str(job.id)})

    assert response.status_code == 404


@pytest.mark.django_db
def test_waiting_readiness_get_does_not_leak_other_users_values(
    auth_client, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """A GET for another user's (resume, job_posting) pair returns 404, not their data."""
    resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(other_user)
    CandidatePreparationSelfAssessment.objects.create(
        user=other_user,
        resume=resume,
        job_posting=job,
        perceived_preparation_percentage=35,
        application_threshold_percentage=80,
    )

    response = auth_client.get(READINESS_URL, {"resume_id": str(resume.id), "job_id": str(job.id)})

    assert response.status_code == 404
