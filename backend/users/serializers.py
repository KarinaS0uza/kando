"""Serializers for the users app.

Defines the serializers used by the authentication and user-registration routes.
"""

from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Single serializer used by all user routes.

    ``is_superuser`` is deliberately excluded from the fields: a superuser is
    only created via ``createsuperuser`` or the Django admin. ``is_staff`` is
    read-only for the same reason — this serializer also handles public
    registration (create with AllowAny), so no privilege field may be writable.
    """

    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        """Configure the model and the exposed fields."""

        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "supabase_uid",
            "is_active",
            "is_staff",
            "date_joined",
            "updated_at",
            "password",
        ]
        read_only_fields = ["id", "is_staff", "date_joined", "updated_at"]

    def validate_password(self, value):
        """Run the configured AUTH_PASSWORD_VALIDATORS against the password.

        Kept as a field-level validator (rather than an object-level
        ``validate``) so password errors are collected and returned together
        with any other field errors — e.g. "email already exists" — in a single
        response, instead of being hidden until the email is corrected. DRF keys
        the resulting message under ``password`` automatically. On update,
        ``self.instance`` lets attribute-similarity checks compare the password
        against the user's own data.
        """
        try:
            django_validate_password(value, user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        """Create a user, setting the password (or leaving it unusable)."""
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update a user, changing the password when one is provided."""
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Validate login credentials only (email and password)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
