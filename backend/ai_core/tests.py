"""Endpoint tests for the ai_core app: prompt list/create/detail/update."""

import uuid

import pytest
from django.urls import reverse

from .models import Prompt

LIST_URL = reverse("ai_core:prompt-list")
CREATE_URL = reverse("ai_core:prompt-create")


def detail_url(pk):
    """Return the retrieve URL for a given prompt id."""
    return reverse("ai_core:prompt-detail", kwargs={"pk": pk})


def update_url(pk):
    """Return the update URL for a given prompt id."""
    return reverse("ai_core:prompt-update", kwargs={"pk": pk})


@pytest.mark.django_db
def test_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(LIST_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_prompts(auth_client):
    """Existing prompts are returned to any authenticated caller."""
    Prompt.objects.create(prompt_description="job_normalization", prompt_detail="v1")

    response = auth_client.get(LIST_URL)

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_rejects_missing_fields(auth_client):
    """Missing required fields return 400."""
    response = auth_client.post(CREATE_URL, {}, format="json")

    assert response.status_code == 400
    assert "prompt_description" in response.data
    assert "prompt_detail" in response.data


@pytest.mark.django_db
def test_create_publishes_a_new_prompt(auth_client):
    """A valid create returns 201 with version 1 and is_active True by default."""
    response = auth_client.post(
        CREATE_URL,
        {"prompt_description": "job_normalization", "prompt_detail": "hello $vaga"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["version"] == 1
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_detail_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(detail_url(uuid.uuid4()))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_existing_prompt(auth_client):
    """An existing prompt is returned by id."""
    prompt = Prompt.objects.create(prompt_description="job_normalization", prompt_detail="v1")

    response = auth_client.get(detail_url(prompt.id))

    assert response.status_code == 200
    assert response.data["id"] == str(prompt.id)


@pytest.mark.django_db
def test_update_returns_404_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.put(
        update_url(uuid.uuid4()),
        {"prompt_description": "x", "prompt_detail": "y"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_update_publishes_a_new_version_when_detail_changes(auth_client):
    """Editing the detail publishes a new, separate version row."""
    prompt = Prompt.objects.create(prompt_description="job_normalization", prompt_detail="v1")

    response = auth_client.put(
        update_url(prompt.id),
        {"prompt_description": "job_normalization", "prompt_detail": "v2"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["version"] == 2
    assert response.data["id"] != str(prompt.id)
    assert Prompt.objects.filter(prompt_description="job_normalization").count() == 2


@pytest.mark.django_db
def test_update_does_not_duplicate_when_detail_is_unchanged(auth_client):
    """Submitting the same detail again does not create a redundant version."""
    prompt = Prompt.objects.create(prompt_description="job_normalization", prompt_detail="v1")

    response = auth_client.put(
        update_url(prompt.id),
        {"prompt_description": "job_normalization", "prompt_detail": "v1"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["id"] == str(prompt.id)
    assert Prompt.objects.filter(prompt_description="job_normalization").count() == 1
