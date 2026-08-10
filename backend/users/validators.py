"""Custom password validators enforcing kando's password policy.

Plugged into ``AUTH_PASSWORD_VALIDATORS`` and run through Django's
``validate_password`` (see users.serializers.UserSerializer).
"""

import re

from django.core.exceptions import ValidationError


class MaximumLengthValidator:
    """Validate that the password is not longer than ``max_length`` characters."""

    def __init__(self, max_length=100):
        self.max_length = max_length

    def validate(self, password, user=None):  # pylint: disable=unused-argument
        """Reject passwords longer than the configured maximum length."""
        if len(password) > self.max_length:
            raise ValidationError(
                f"A senha não pode exceder {self.max_length} caracteres.",
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        """Return the human-readable requirement for this validator."""
        return f"Sua senha não pode exceder {self.max_length} caracteres."


class ComplexityValidator:
    """Validate that the password mixes upper, lower, digit and special chars."""

    def validate(self, password, user=None):  # pylint: disable=unused-argument
        """Reject passwords missing any required character class.

        The error names only the classes actually missing, so the user gets a
        specific, actionable message instead of the full rule every time.
        """
        missing = []
        if not re.search(r"[A-Z]", password):
            missing.append("uma letra maiúscula")
        if not re.search(r"[a-z]", password):
            missing.append("uma letra minúscula")
        if not re.search(r"[0-9]", password):
            missing.append("um número")
        if not re.search(r"[^A-Za-z0-9]", password):
            missing.append("um caractere especial")

        if missing:
            raise ValidationError(
                "A senha deve conter pelo menos " + ", ".join(missing) + ".",
                code="password_not_complex",
            )

    def get_help_text(self):
        """Return the human-readable requirement for this validator."""
        return (
            "Sua senha deve conter pelo menos uma letra maiúscula, uma letra "
            "minúscula, um número e um caractere especial."
        )
