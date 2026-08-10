"""Shared pytest fixtures for endpoint tests across all apps."""

# Pytest injects fixtures by matching function argument names, which
# intentionally references fixture functions defined in this module.
# pylint: disable=redefined-outer-name

import uuid

import pytest
from rest_framework.test import APIClient

from assessments.models import Assessment, AssessmentResult
from jobs.models import JobPostingNormalization, JobPostingSubmission
from matching.models import MatchResult
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
        structured_data = {"job_title": "Developer", **structured_data_overrides}
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
            "calculated_seniority": "mid_level",
            **structured_data_overrides,
        }
        ResumeNormalization.objects.create(
            resume=resume, success=True, structured_data=structured_data
        )
        return resume

    return create


@pytest.fixture
def match_result_factory(db):  # pylint: disable=unused-argument
    """Return a callable creating a successful MatchResult for a resume/job pair."""

    def create(resume, job_posting, **structured_data_overrides):
        structured_data = {
            "resume_title": "Developer",
            "job_title": "Developer",
            "compatibility_score": 80,
            "matching_skills": ["React"],
            "missing_skills": ["TypeScript"],
            "strengths": [],
            "improvement_areas": [],
            **structured_data_overrides,
        }
        return MatchResult.objects.create(
            resume=resume,
            job_posting=job_posting,
            success=True,
            overall_match_score=structured_data["compatibility_score"],
            seniority_compatible=True,
            structured_data=structured_data,
        )

    return create


@pytest.fixture
def graded_assessment_factory(db):  # pylint: disable=unused-argument
    """Return a callable creating a successful, graded Assessment for a resume/job pair.

    Returns the AssessmentResult; the parent Assessment is reachable via
    ``assessment_result.assessment``.
    """

    def create(resume, job_posting, **overrides):
        assessment_structured_data = overrides.pop("assessment_structured_data", None) or {
            "blocks": [
                {"topic": "React", "questions": [{"id": "B1Q1"}, {"id": "B1Q2"}]},
                {"topic": "Node.js", "questions": [{"id": "B2Q1"}]},
            ]
        }
        assessment = Assessment.objects.create(
            resume=resume,
            job_posting=job_posting,
            success=True,
            structured_data=assessment_structured_data,
        )
        result_structured_data = overrides.pop("result_structured_data", None) or {
            "evaluations": [
                {
                    "id": "B1Q1",
                    "evaluation": {
                        "score": 80,
                        "skills": [{"name": "React", "score": 85, "evidence": []}],
                    },
                },
                {
                    "id": "B1Q2",
                    "evaluation": {
                        "score": 60,
                        "skills": [{"name": "React", "score": 60, "evidence": []}],
                    },
                },
                {
                    "id": "B2Q1",
                    "evaluation": {
                        "score": 40,
                        "skills": [{"name": "Node.js", "score": 40, "evidence": []}],
                    },
                },
            ],
            "aggregation": {
                "evaluation": {
                    "score": 60,
                    "skills": [
                        {"name": "React", "score": 72, "evidence": []},
                        {"name": "Node.js", "score": 40, "evidence": []},
                    ],
                    "strengths": [],
                    "weaknesses": [],
                    "feedback": "Média de 3 de 3 questions avaliadas.",
                }
            },
        }
        defaults = {
            "success": True,
            "score": 60,
            "answers": [],
            "structured_data": result_structured_data,
            **overrides,
        }
        return AssessmentResult.objects.create(assessment=assessment, **defaults)

    return create
