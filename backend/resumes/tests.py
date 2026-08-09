"""Endpoint tests for the resumes app: resume list/create/detail/delete."""

import uuid

import pytest
from django.urls import reverse

from .models import ResumeSubmission

LIST_URL = reverse("resumes:resume-list-create")


def detail_url(pk):
    """Return the detail/delete URL for a given resume id."""
    return reverse("resumes:resume-detail", kwargs={"pk": pk})


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_only_owned_resumes(auth_client, user, other_user, normalized_resume_factory):
    """Resumes belonging to other users are excluded from the list."""
    normalized_resume_factory(user)
    normalized_resume_factory(other_user)

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
        "resumes.views.normalize_resume",
        lambda text: {"resume_title": "Backend Developer", "skills_tecnicas": []},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "y" * 200}, format="json"
    )

    assert response.status_code == 201
    assert response.data["normalization"]["success"] is True
    resume = ResumeSubmission.objects.get(id=response.data["id"])
    assert resume.submitted_by_id == user.id


@pytest.mark.django_db
def test_create_rejects_text_misclassified_as_not_a_resume(auth_client, monkeypatch):
    """A positive entrada_invalida verdict returns 400 and persists nothing."""
    monkeypatch.setattr(
        "resumes.views.normalize_resume",
        lambda text: {"entrada_invalida": True, "motivo_entrada_invalida": "Parece uma vaga."},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "y" * 200}, format="json"
    )

    assert response.status_code == 400
    assert ResumeSubmission.objects.count() == 0


@pytest.mark.django_db
def test_create_stores_failed_normalization_without_blocking_creation(auth_client, monkeypatch):
    """An LLM-side error still saves the resume, with a failed normalization row."""
    monkeypatch.setattr(
        "resumes.views.normalize_resume",
        lambda text: {"error": "timeout", "retryable": True},
    )

    response = auth_client.post(
        LIST_URL, {"source": "text", "raw_text": "y" * 200}, format="json"
    )

    assert response.status_code == 201
    assert response.data["normalization"]["success"] is False


@pytest.mark.django_db
def test_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_404_for_other_users_resume(auth_client, other_user, normalized_resume_factory):
    """A resume owned by another user is not visible."""
    resume = normalized_resume_factory(other_user)

    response = auth_client.get(detail_url(resume.id))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_owned_resume(auth_client, user, normalized_resume_factory):
    """An owned resume is returned with its normalization data."""
    resume = normalized_resume_factory(user)

    response = auth_client.get(detail_url(resume.id))

    assert response.status_code == 200
    assert response.data["id"] == str(resume.id)


@pytest.mark.django_db
def test_delete_removes_owned_resume(auth_client, user, normalized_resume_factory):
    """A successful delete returns 204 and the row no longer exists."""
    resume = normalized_resume_factory(user)

    response = auth_client.delete(detail_url(resume.id))

    assert response.status_code == 204
    assert not ResumeSubmission.objects.filter(id=resume.id).exists()


@pytest.mark.django_db
def test_delete_returns_404_for_other_users_resume(auth_client, other_user, normalized_resume_factory):
    """Deleting another user's resume is blocked and nothing is removed."""
    resume = normalized_resume_factory(other_user)

    response = auth_client.delete(detail_url(resume.id))

    assert response.status_code == 404
    assert ResumeSubmission.objects.filter(id=resume.id).exists()
