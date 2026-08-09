"""Endpoint tests for the users app: login and user CRUD routes."""

import uuid

import pytest
from django.urls import reverse

from .models import User

VALID_PASSWORD = "Test#Passw0rd!"


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(api_client, user):
    """A wrong password returns 401 with no tokens."""
    response = api_client.post(
        reverse("login"), {"email": user.email, "password": "wrong"}, format="json"
    )

    assert response.status_code == 401
    assert "access" not in response.data


@pytest.mark.django_db
def test_login_returns_tokens_for_valid_credentials(api_client, user):
    """Correct credentials return an access and refresh token."""
    response = api_client.post(
        reverse("login"), {"email": user.email, "password": VALID_PASSWORD}, format="json"
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user_id"] == str(user.id)


@pytest.mark.django_db
def test_user_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(reverse("user-list"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_list_currently_returns_every_user(auth_client, user, other_user):
    """Any authenticated user currently sees every account, not just their own.

    Documents the known temporary IsAuthenticated scope; expected to start
    failing once the users views move to IsAdminUser/ownership scoping.
    """
    response = auth_client.get(reverse("user-list"))

    assert response.status_code == 200
    returned_ids = {row["id"] for row in response.data}
    assert {str(user.id), str(other_user.id)} <= returned_ids


@pytest.mark.django_db
def test_user_detail_requires_authentication(api_client, user):
    """An anonymous request is rejected."""
    response = api_client.get(reverse("user-detail", kwargs={"pk": user.id}))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_detail_currently_returns_any_user(auth_client, other_user):
    """Any authenticated user can currently read another user's detail record."""
    response = auth_client.get(reverse("user-detail", kwargs={"pk": other_user.id}))

    assert response.status_code == 200
    assert response.data["id"] == str(other_user.id)


@pytest.mark.django_db
def test_user_detail_not_found_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(reverse("user-detail", kwargs={"pk": uuid.uuid4()}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_create_rejects_invalid_data(api_client):
    """Missing required fields return 400 with field-level errors."""
    response = api_client.post(
        reverse("user-create"), {"email": "not-an-email"}, format="json"
    )

    assert response.status_code == 400
    assert "email" in response.data
    assert "full_name" in response.data


@pytest.mark.django_db
def test_user_create_rejects_weak_password(api_client):
    """A password missing complexity requirements is rejected."""
    response = api_client.post(
        reverse("user-create"),
        {"email": "new-user@example.invalid", "full_name": "New User", "password": "weak"},
        format="json",
    )

    assert response.status_code == 400
    assert "password" in response.data


@pytest.mark.django_db
def test_user_create_succeeds_with_valid_data(api_client):
    """A valid registration returns 201 and never echoes is_staff as writable."""
    response = api_client.post(
        reverse("user-create"),
        {
            "email": "new-user@example.invalid",
            "full_name": "New User",
            "password": VALID_PASSWORD,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["is_staff"] is False
    created = User.objects.get(id=response.data["id"])
    assert created.check_password(VALID_PASSWORD)


@pytest.mark.django_db
def test_user_update_requires_authentication(api_client, user):
    """An anonymous request is rejected."""
    response = api_client.patch(
        reverse("user-update", kwargs={"pk": user.id}), {"full_name": "X"}, format="json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_update_currently_allows_editing_another_user(auth_client, other_user):
    """Any authenticated user can currently change another user's password.

    Documents the known IDOR in UserUpdateView; expected to start failing
    once update access is restricted to the owner or an admin.
    """
    response = auth_client.patch(
        reverse("user-update", kwargs={"pk": other_user.id}),
        {"password": "NewOwner#Passw0rd!"},
        format="json",
    )

    assert response.status_code == 200
    other_user.refresh_from_db()
    assert other_user.check_password("NewOwner#Passw0rd!")


@pytest.mark.django_db
def test_user_update_not_found_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.patch(
        reverse("user-update", kwargs={"pk": uuid.uuid4()}), {"full_name": "X"}, format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_delete_requires_authentication(api_client, user):
    """An anonymous request is rejected."""
    response = api_client.delete(reverse("user-delete", kwargs={"pk": user.id}))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_delete_removes_target_user(auth_client, other_user):
    """A successful delete returns 204 and the row no longer exists."""
    response = auth_client.delete(reverse("user-delete", kwargs={"pk": other_user.id}))

    assert response.status_code == 204
    assert not User.objects.filter(id=other_user.id).exists()


@pytest.mark.django_db
def test_user_delete_not_found_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.delete(reverse("user-delete", kwargs={"pk": uuid.uuid4()}))

    assert response.status_code == 404
