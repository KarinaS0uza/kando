"""Managers for the users app.

Defines the custom manager the User model uses to create users and superusers
by email instead of username.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for the email-based User model.

    Overrides user creation to use email as the identifier and to handle an
    optional password (users coming from Supabase may have no local password).
    """

    use_in_migrations = True

    def create_and_save_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password.

        Shared by create_user and create_superuser. With no password the user is
        saved with an unusable password (e.g. authentication handled via Supabase).
        """
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create a regular user (non-staff, non-superuser) by default."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self.create_and_save_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser, requiring the staff/superuser flags and a password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")
        if not password:
            raise ValueError("A superuser must have a password.")

        return self.create_and_save_user(email, password, **extra_fields)
