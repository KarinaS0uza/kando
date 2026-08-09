"""Models for the users app.

Defines the custom User model used for authentication, supporting both locally
created users (e.g. via createsuperuser) and users authenticated through
Supabase Auth.
"""

import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user that authenticates by email instead of username.

    Supports both locally created users (e.g. Django admin/superusers) and users
    linked to an external Supabase Auth account via ``supabase_uid``.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    # Links the local record to a user authenticated via Supabase Auth. Null for
    # users that only exist locally (e.g. created via createsuperuser).
    supabase_uid = models.UUIDField(unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    # Use "email" as the unique login identifier instead of the default
    # "username" field.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Metadata options for the User model."""
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        """Return the user's email as the readable representation."""
        return self.email
