"""Serializers for the users app.

Defines the serializers used by the authentication and user-registration routes.
"""

from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import User

PASSWORD_ERROR_MESSAGES = {
    "password_too_short": "A senha deve conter no mínimo {min_length} caracteres.",
    "password_too_common": "Esta senha é muito comum e fácil de adivinhar.",
    "password_entirely_numeric": "A senha não pode ser inteiramente numérica.",
    "password_too_similar": (
        "A senha não pode conter informações pessoais como nome ou e-mail."
    ),
}


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
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "invalid": "Por favor, insira um endereço de e-mail válido."
                },
                # DRF's automatic uniqueness validator produces a mixed-
                # language message ("user com este email já existe.").
                # validate_email below replaces it with a proper one, for
                # both create (also pre-checked in to_internal_value, ahead
                # of the generic credentials message) and update.
                "validators": [],
            },
            "supabase_uid": {"validators": []},
        }

    def to_internal_value(self, data):
        """Validate registration credentials in a predictable sequence.

        An existing email, a malformed email, and any password problem
        (blank, whitespace-only, or failing a configured strength validator)
        are each reported specifically, without naming the exact rule that
        failed for the latter two.
        """
        if self.instance is None:
            email = data.get("email")
            if isinstance(email, str) and User.objects.filter(
                email__iexact=email.strip()
            ).exists():
                raise serializers.ValidationError(
                    {"email": ["Este e-mail já está cadastrado em nosso sistema."]}
                )

            password = data.get("password")
            if not isinstance(password, str) or not password.strip():
                raise serializers.ValidationError({"password": ["Senha inválida."]})
            try:
                self.validate_password(self.fields["password"].run_validation(password))
            except serializers.ValidationError as exc:
                raise serializers.ValidationError(
                    {"password": ["Senha inválida."]}
                ) from exc

            try:
                self.fields["email"].run_validation(email)
            except serializers.ValidationError as exc:
                raise serializers.ValidationError(
                    {"email": ["E-mail inválido."]}
                ) from exc
        return super().to_internal_value(data)

    def validate_password(self, value):
        """Run the configured AUTH_PASSWORD_VALIDATORS against the password.

        Django's error codes are remapped to the project's standard messages
        (``PASSWORD_ERROR_MESSAGES``); validators without a mapped code (e.g.
        ``ComplexityValidator``) keep their own message. These messages reach
        the client as-is on update; on registration, ``to_internal_value``
        catches the exception instead and replaces it with the same "Senha
        inválida." message used for a blank password, without naming the
        specific rule that failed. ``self.instance`` lets attribute-
        similarity checks compare the password against the user's own data.
        """
        try:
            django_validate_password(value, user=self.instance)
        except DjangoValidationError as exc:
            messages = [
                PASSWORD_ERROR_MESSAGES[error.code] % (error.params or {})
                if error.code in PASSWORD_ERROR_MESSAGES
                else error.message % (error.params or {})
                for error in exc.error_list
            ]
            raise serializers.ValidationError(messages) from exc
        return value

    def validate_email(self, value):
        """Reject an email already used by another account.

        Covers update (create's duplicate case is already caught earlier, in
        ``to_internal_value``, before this ever runs) now that DRF's
        automatic uniqueness validator is disabled for this field.
        """
        email = value.strip()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Este e-mail já está cadastrado em nosso sistema."
            )
        return email

    def validate_supabase_uid(self, value):
        """Reject a supabase_uid already linked to another account."""
        if value is None:
            return value
        queryset = User.objects.filter(supabase_uid=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Este supabase_uid já está vinculado a outra conta."
            )
        return value

    def validate_full_name(self, value):
        """Require a first and last name, not just a single word."""
        if len(value.split()) < 2:
            raise serializers.ValidationError(
                "Por favor, insira seu nome completo (nome e sobrenome)."
            )
        return value

    def create(self, validated_data):
        """Create a user with the validated required password."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
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
