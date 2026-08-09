"""Shared pytest fixtures for endpoint tests across all apps."""

import uuid

import pytest
from rest_framework.test import APIClient

from jobs.models import JobPostingNormalization, JobPostingSubmission
from resumes.models import ResumeNormalization, ResumeSubmission
from users.models import User

VALID_PASSWORD = "Test#Passw0rd!"


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def user_factory(db):  # pylint: disable=unused-argument
    """Return a callable that creates a User with sensible defaults."""

    def create_user(**overrides):
        overrides.setdefault("email", f"user-{uuid.uuid4()}@example.invalid")
        overrides.setdefault("password", VALID_PASSWORD)
        overrides.setdefault("full_name", "Test User")
        return User.objects.create_user(**overrides)

    return create_user


@pytest.fixture
def user(user_factory):
    """Return one persisted test user."""
    return user_factory()


@pytest.fixture
def other_user(user_factory):
    """Return a second persisted test user, distinct from `user`."""
    return user_factory()


@pytest.fixture
def auth_client(api_client, user):
    """Return an API client authenticated as `user`."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def normalized_job_posting_factory(db):  # pylint: disable=unused-argument
    """Return a callable creating a successfully normalized job posting for an owner."""

    def create(owner, **structured_data_overrides):
        job_posting = JobPostingSubmission.objects.create(
            submitted_by=owner, source="text", raw_text="x" * 200
        )
        structured_data = {"job_posting_title": "Developer", **structured_data_overrides}
        JobPostingNormalization.objects.create(
            job_posting=job_posting, success=True, structured_data=structured_data
        )
        return job_posting

    return create


@pytest.fixture
def normalized_resume_factory(db):  # pylint: disable=unused-argument
    """Return a callable creating a successfully normalized resume for an owner."""

    def create(owner, **structured_data_overrides):
        resume = ResumeSubmission.objects.create(
            submitted_by=owner, source="text", raw_text="y" * 200
        )
        structured_data = {
            "resume_title": "Developer",
            "senioridade_estimada_por_metricas": "pleno",
            **structured_data_overrides,
        }
        ResumeNormalization.objects.create(
            resume=resume, success=True, structured_data=structured_data
        )
        return resume

    return create
