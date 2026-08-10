"""Endpoint tests for the assessments app: generation, detail/delete, and grading."""

import uuid

import pytest
from django.urls import reverse

from resumes.models import ResumeSubmission

from .models import Assessment

LIST_URL = reverse("assessments:assessment-list-create")


def detail_url(pk):
    """Return the detail/delete URL for a given assessment id."""
    return reverse("assessments:assessment-detail", kwargs={"pk": pk})


def result_url(pk):
    """Return the grading URL for a given assessment id."""
    return reverse("assessments:assessment-result-create", kwargs={"pk": pk})


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_only_owned_assessments(
    auth_client, user, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """Assessments for another user's resume are excluded from the list."""
    own_resume = normalized_resume_factory(user)
    own_job = normalized_job_posting_factory(user)
    Assessment.objects.create(resume=own_resume, job_posting=own_job, success=True)

    other_resume = normalized_resume_factory(other_user)
    other_job = normalized_job_posting_factory(other_user)
    Assessment.objects.create(resume=other_resume, job_posting=other_job, success=True)

    response = auth_client.get(LIST_URL)

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_rejects_unknown_resume_id(auth_client, user, normalized_job_posting_factory):
    """A resume_id that does not belong to the caller returns 400."""
    job = normalized_job_posting_factory(user)

    response = auth_client.post(
        LIST_URL, {"resume_id": str(uuid.uuid4()), "job_id": str(job.id)}, format="json"
    )

    assert response.status_code == 400
    assert "resume_id" in response.data


@pytest.mark.django_db
def test_create_rejects_unnormalized_resume(auth_client, user, normalized_job_posting_factory):
    """A resume without a successful normalization cannot generate an assessment."""
    unnormalized_resume = ResumeSubmission.objects.create(
        submitted_by=user, source="text", raw_text="y" * 200
    )
    job = normalized_job_posting_factory(user)

    response = auth_client.post(
        LIST_URL,
        {"resume_id": str(unnormalized_resume.id), "job_id": str(job.id)},
        format="json",
    )

    assert response.status_code == 400
    assert "resume_id" in response.data


@pytest.mark.django_db
def test_create_succeeds_and_rerun_upserts(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory, monkeypatch
):
    """A successful generation is created once, then updated in place on rerun."""
    monkeypatch.setattr(
        "assessments.views.generate_assessment",
        lambda resume_data, job_data: {"blocks": [{"questions": [{"id": "B1Q1"}]}]},
    )
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    payload = {"resume_id": str(resume.id), "job_id": str(job.id)}

    first_response = auth_client.post(LIST_URL, payload, format="json")
    assert first_response.status_code == 201
    assert first_response.data["questions"] == [{"id": "B1Q1"}]

    second_response = auth_client.post(LIST_URL, payload, format="json")
    assert second_response.status_code == 200
    assert Assessment.objects.filter(resume=resume, job_posting=job).count() == 1


@pytest.mark.django_db
def test_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_404_for_other_users_assessment(
    auth_client, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """An assessment for another user's resume is not visible."""
    resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(other_user)
    assessment = Assessment.objects.create(resume=resume, job_posting=job, success=True)

    response = auth_client.get(detail_url(assessment.id))

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_removes_owned_assessment(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """A successful delete returns 204 and the row no longer exists."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    assessment = Assessment.objects.create(resume=resume, job_posting=job, success=True)

    response = auth_client.delete(detail_url(assessment.id))

    assert response.status_code == 204
    assert not Assessment.objects.filter(id=assessment.id).exists()


@pytest.mark.django_db
def test_result_returns_404_for_unknown_assessment(auth_client):
    """A nonexistent assessment id returns 404."""
    response = auth_client.post(
        result_url(uuid.uuid4()), {"answers": [{"id": "B1Q1", "answer": "x"}]}, format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_result_requires_a_generated_assessment(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """Grading an assessment that was never successfully generated returns 400."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    assessment = Assessment.objects.create(resume=resume, job_posting=job, success=False)

    response = auth_client.post(
        result_url(assessment.id), {"answers": [{"id": "B1Q1", "answer": "x"}]}, format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_result_rejects_empty_answers(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """At least one answer is required."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    assessment = Assessment.objects.create(
        resume=resume, job_posting=job, success=True, structured_data={"blocks": []}
    )

    response = auth_client.post(result_url(assessment.id), {"answers": []}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_result_grades_answers_and_upserts(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory, monkeypatch
):
    """A successful grading is created once, then updated in place on rerun."""
    monkeypatch.setattr(
        "assessments.views.grade_assessment",
        lambda assessment, submitted_answers: {
            "success": True,
            "score": 90,
            "answers": submitted_answers,
            "structured_data": {"evaluations": [], "aggregation": {}},
            "error_message": None,
        },
    )
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    assessment = Assessment.objects.create(
        resume=resume,
        job_posting=job,
        success=True,
        structured_data={"blocks": [{"questions": [{"id": "B1Q1"}]}]},
    )
    payload = {"answers": [{"id": "B1Q1", "answer": "minha answer"}]}

    first_response = auth_client.post(result_url(assessment.id), payload, format="json")
    assert first_response.status_code == 201
    assert first_response.data["result"]["score"] == 90

    second_response = auth_client.post(result_url(assessment.id), payload, format="json")
    assert second_response.status_code == 200
