"""Endpoint tests for the matching app: match list/create/detail/delete."""

import uuid

import pytest
from django.urls import reverse

from resumes.models import ResumeSubmission

from .models import MatchResult

LIST_URL = reverse("matching:match-list-create")


def detail_url(pk):
    """Return the detail/delete URL for a given match result id."""
    return reverse("matching:match-detail", kwargs={"pk": pk})


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_only_owned_matches(
    auth_client, user, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """Match results for resumes belonging to other users are excluded."""
    own_resume = normalized_resume_factory(user)
    own_job = normalized_job_posting_factory(user)
    MatchResult.objects.create(resume=own_resume, job_posting=own_job, success=True)

    other_resume = normalized_resume_factory(other_user)
    other_job = normalized_job_posting_factory(other_user)
    MatchResult.objects.create(resume=other_resume, job_posting=other_job, success=True)

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
    """A resume without a successful normalization cannot be matched."""
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
    """A successful match is created once, then updated in place on rerun."""
    monkeypatch.setattr(
        "matching.views.analyze_match",
        lambda resume_data, job_data: {
            "compatibility_score": 80,
            "seniority_compatible": True,
        },
    )
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    payload = {"resume_id": str(resume.id), "job_id": str(job.id)}

    first_response = auth_client.post(LIST_URL, payload, format="json")
    assert first_response.status_code == 201
    assert first_response.data["overall_match_score"] == 80

    second_response = auth_client.post(LIST_URL, payload, format="json")
    assert second_response.status_code == 200
    assert MatchResult.objects.filter(resume=resume, job_posting=job).count() == 1


@pytest.mark.django_db
def test_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_404_for_other_users_match(
    auth_client, other_user, normalized_resume_factory, normalized_job_posting_factory
):
    """A match result for another user's resume is not visible."""
    resume = normalized_resume_factory(other_user)
    job = normalized_job_posting_factory(other_user)
    match = MatchResult.objects.create(resume=resume, job_posting=job, success=True)

    response = auth_client.get(detail_url(match.id))

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_removes_owned_match(
    auth_client, user, normalized_resume_factory, normalized_job_posting_factory
):
    """A successful delete returns 204 and the row no longer exists."""
    resume = normalized_resume_factory(user)
    job = normalized_job_posting_factory(user)
    match = MatchResult.objects.create(resume=resume, job_posting=job, success=True)

    response = auth_client.delete(detail_url(match.id))

    assert response.status_code == 204
    assert not MatchResult.objects.filter(id=match.id).exists()
