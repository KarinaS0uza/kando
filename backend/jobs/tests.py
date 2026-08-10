"""Endpoint tests for the jobs app: job posting list/create/detail/delete."""

import uuid

import pytest
from django.urls import reverse

from .models import JobPostingSubmission
from .services.job_llm_normalization import normalize_job_posting

LIST_URL = reverse("jobs:job-posting-list-create")


def test_normalization_canonicalizes_legacy_nested_job_title(monkeypatch):
    """An older prompt response is persisted with only the canonical title key."""
    monkeypatch.setattr(
        "jobs.services.job_llm_normalization.run_prompt_safe",
        lambda *args, **kwargs: {
            "vaga": {"titulo": "Backend Developer", "empresa": "Acme"}
        },
    )

    result = normalize_job_posting("valid job posting")

    assert result["job_title"] == "Backend Developer"
    assert "title" not in result["job"]
    assert "job_posting_title" not in result


def detail_url(pk):
    """Return the detail/delete URL for a given job posting id."""
    return reverse("jobs:job-posting-detail", kwargs={"pk": pk})


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_only_owned_postings(auth_client, user, other_user, normalized_job_posting_factory):
    """Postings belonging to other users are excluded from the list."""
    normalized_job_posting_factory(user)
    normalized_job_posting_factory(other_user)

    response = auth_client.get(LIST_URL)

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_rejects_invalid_source(auth_client):
    """An unknown source choice returns 400."""
    response = auth_client.post(LIST_URL, {"source": "bogus"}, format="json")

    assert response.status_code == 400
    assert "source" in response.data


@pytest.mark.django_db
def test_create_rejects_text_below_minimum_length(auth_client):
    """Text shorter than the minimum is rejected before any normalization call."""
    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "too short"}, format="json"
    )

    assert response.status_code == 400
    assert "raw_text" in response.data


@pytest.mark.django_db
def test_create_persists_successful_normalization(auth_client, user, monkeypatch):
    """A valid submission is saved with its normalization result."""
    monkeypatch.setattr(
        "jobs.views.normalize_job_posting",
        lambda text: {"is_job_posting": True, "job_title": "Backend Developer"},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "x" * 200}, format="json"
    )

    assert response.status_code == 201
    assert response.data["normalization"]["success"] is True
    posting = JobPostingSubmission.objects.get(id=response.data["id"])
    assert posting.submitted_by_id == user.id


@pytest.mark.django_db
def test_create_rejects_text_misclassified_as_not_a_job_posting(auth_client, monkeypatch):
    """A negative is_job_posting verdict returns 400 and persists nothing."""
    monkeypatch.setattr(
        "jobs.views.normalize_job_posting",
        lambda text: {"is_job_posting": False},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "x" * 200}, format="json"
    )

    assert response.status_code == 400
    assert JobPostingSubmission.objects.count() == 0


@pytest.mark.django_db
def test_create_stores_failed_normalization_without_blocking_creation(auth_client, monkeypatch):
    """An LLM-side error still saves the posting, with a failed normalization row."""
    monkeypatch.setattr(
        "jobs.views.normalize_job_posting",
        lambda text: {"error": "timeout", "retryable": True},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "x" * 200}, format="json"
    )

    assert response.status_code == 201
    assert response.data["normalization"]["success"] is False


@pytest.mark.django_db
def test_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_404_for_other_users_posting(auth_client, other_user, normalized_job_posting_factory):
    """A posting owned by another user is not visible."""
    posting = normalized_job_posting_factory(other_user)

    response = auth_client.get(detail_url(posting.id))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_owned_posting(auth_client, user, normalized_job_posting_factory):
    """An owned posting is returned with its normalization data."""
    posting = normalized_job_posting_factory(user)

    response = auth_client.get(detail_url(posting.id))

    assert response.status_code == 200
    assert response.data["id"] == str(posting.id)


@pytest.mark.django_db
def test_update_method_not_allowed(auth_client, user, normalized_job_posting_factory):
    """PUT is not a supported method on the detail route."""
    posting = normalized_job_posting_factory(user)

    response = auth_client.put(detail_url(posting.id), {}, format="json")

    assert response.status_code == 405


@pytest.mark.django_db
def test_delete_removes_owned_posting(auth_client, user, normalized_job_posting_factory):
    """A successful delete returns 204 and the row no longer exists."""
    posting = normalized_job_posting_factory(user)

    response = auth_client.delete(detail_url(posting.id))

    assert response.status_code == 204
    assert not JobPostingSubmission.objects.filter(id=posting.id).exists()


@pytest.mark.django_db
def test_delete_returns_404_for_other_users_posting(auth_client, other_user, normalized_job_posting_factory):
    """Deleting another user's posting is blocked and nothing is removed."""
    posting = normalized_job_posting_factory(other_user)

    response = auth_client.delete(detail_url(posting.id))

    assert response.status_code == 404
    assert JobPostingSubmission.objects.filter(id=posting.id).exists()
