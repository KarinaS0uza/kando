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
    assert response.data == {"email": "Credenciais inválidas."}
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
def test_login_rejects_malformed_email(api_client):
    """A malformed email returns the same generic 401 as a wrong password."""
    response = api_client.post(
        reverse("login"),
        {"email": "not-an-email", "password": "whatever"},
        format="json",
    )

    assert response.status_code == 401
    assert response.data == {"email": "Credenciais inválidas."}


@pytest.mark.django_db
def test_user_list_requires_authentication(api_client):
    """An anonymous request is rejected."""
    response = api_client.get(reverse("user-list"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_list_forbidden_for_non_admin(auth_client):
    """A regular authenticated user cannot list all accounts."""
    response = auth_client.get(reverse("user-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_list_returns_every_user_for_admin(admin_client, user, other_user):
    """An admin sees every account."""
    response = admin_client.get(reverse("user-list"))

    assert response.status_code == 200
    returned_ids = {row["id"] for row in response.data}
    assert {str(user.id), str(other_user.id)} <= returned_ids


@pytest.mark.django_db
def test_user_detail_requires_authentication(api_client, user):
    """An anonymous request is rejected."""
    response = api_client.get(reverse("user-detail", kwargs={"pk": user.id}))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_detail_forbidden_for_other_user(auth_client, other_user):
    """A regular user cannot read another user's detail record."""
    response = auth_client.get(reverse("user-detail", kwargs={"pk": other_user.id}))

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_detail_allows_own_record(auth_client, user):
    """A regular user can read their own detail record."""
    response = auth_client.get(reverse("user-detail", kwargs={"pk": user.id}))

    assert response.status_code == 200
    assert response.data["id"] == str(user.id)


@pytest.mark.django_db
def test_user_detail_allows_admin_for_any_user(admin_client, other_user):
    """An admin can read any user's detail record."""
    response = admin_client.get(reverse("user-detail", kwargs={"pk": other_user.id}))

    assert response.status_code == 200
    assert response.data["id"] == str(other_user.id)


@pytest.mark.django_db
def test_user_detail_not_found_for_unknown_id(auth_client):
    """A nonexistent id returns 404."""
    response = auth_client.get(reverse("user-detail", kwargs={"pk": uuid.uuid4()}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_create_rejects_malformed_email(api_client):
    """A malformed email is rejected specifically."""
    response = api_client.post(
        reverse("user-create"),
        {"email": "not-an-email", "full_name": "New User", "password": VALID_PASSWORD},
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {"email": ["E-mail inválido."]}


@pytest.mark.django_db
def test_user_create_rejects_weak_password(api_client):
    """A password missing complexity requirements is rejected specifically."""
    response = api_client.post(
        reverse("user-create"),
        {"email": "new-user@example.invalid", "full_name": "New User", "password": "weak"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {"password": ["Senha inválida."]}


@pytest.mark.django_db
def test_user_create_requires_password(api_client):
    """Public registration cannot create a user without local credentials."""
    response = api_client.post(
        reverse("user-create"),
        {"email": "no-password@example.invalid", "full_name": "No Password"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {"password": ["Senha inválida."]}
    assert not User.objects.filter(email="no-password@example.invalid").exists()


@pytest.mark.django_db
def test_user_create_rejects_whitespace_only_password(api_client):
    """A password made only of whitespace is treated the same as blank."""
    response = api_client.post(
        reverse("user-create"),
        {
            "email": "whitespace-password@example.invalid",
            "full_name": "New User",
            "password": "   ",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {"password": ["Senha inválida."]}
    assert not User.objects.filter(email="whitespace-password@example.invalid").exists()


@pytest.mark.django_db
def test_user_create_reports_existing_email_specifically(user, api_client):
    """An existing email is named explicitly, taking priority over password errors."""
    response = api_client.post(
        reverse("user-create"),
        {
            "email": user.email.upper(),
            "full_name": user.full_name,
            "password": "kkkkkkkk",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {
        "email": ["Este e-mail já está cadastrado em nosso sistema."]
    }


@pytest.mark.django_db
def test_user_create_rejects_single_word_full_name(api_client):
    """A full_name without a surname is rejected."""
    response = api_client.post(
        reverse("user-create"),
        {
            "email": "single-name@example.invalid",
            "full_name": "Ana",
            "password": VALID_PASSWORD,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "full_name" in response.data
    assert not User.objects.filter(email="single-name@example.invalid").exists()


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
def test_user_update_forbidden_for_non_admin(auth_client, other_user):
    """A regular user cannot update another user's record."""
    response = auth_client.patch(
        reverse("user-update", kwargs={"pk": other_user.id}),
        {"password": "NewOwner#Passw0rd!"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_update_forbidden_for_own_record(auth_client, user):
    """A regular user cannot update even their own record; only an admin can."""
    response = auth_client.patch(
        reverse("user-update", kwargs={"pk": user.id}), {"full_name": "X Y"}, format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_update_allows_admin_to_edit_any_user(admin_client, other_user):
    """An admin can update another user's record."""
    response = admin_client.patch(
        reverse("user-update", kwargs={"pk": other_user.id}),
        {"password": "NewOwner#Passw0rd!"},
        format="json",
    )

    assert response.status_code == 200
    other_user.refresh_from_db()
    assert other_user.check_password("NewOwner#Passw0rd!")


@pytest.mark.django_db
def test_user_update_not_found_for_unknown_id(admin_client):
    """A nonexistent id returns 404 for an admin."""
    response = admin_client.patch(
        reverse("user-update", kwargs={"pk": uuid.uuid4()}), {"full_name": "X"}, format="json"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_delete_requires_authentication(api_client, user):
    """An anonymous request is rejected."""
    response = api_client.delete(reverse("user-delete", kwargs={"pk": user.id}))

    assert response.status_code == 401


@pytest.mark.django_db
def test_user_delete_forbidden_for_non_admin(auth_client, other_user):
    """A regular user cannot delete another user's account."""
    response = auth_client.delete(reverse("user-delete", kwargs={"pk": other_user.id}))

    assert response.status_code == 403
    assert User.objects.filter(id=other_user.id).exists()


@pytest.mark.django_db
def test_user_delete_removes_target_user_for_admin(admin_client, other_user):
    """A successful admin delete returns 204 and the row no longer exists."""
    response = admin_client.delete(reverse("user-delete", kwargs={"pk": other_user.id}))

    assert response.status_code == 204
    assert not User.objects.filter(id=other_user.id).exists()


@pytest.mark.django_db
def test_user_delete_not_found_for_unknown_id(admin_client):
    """A nonexistent id returns 404 for an admin."""
    response = admin_client.delete(reverse("user-delete", kwargs={"pk": uuid.uuid4()}))

    assert response.status_code == 404
