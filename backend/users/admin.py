"""Admin for the users app.

Configures the Django admin interface for the custom User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for the email-based User model."""

    ordering = ["email"]
    list_display = ["email", "full_name", "supabase_uid", "is_staff", "is_active"]
    search_fields = ["email", "full_name", "supabase_uid"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {"fields": ("full_name",)}),
        ("Supabase", {"fields": ("supabase_uid",)}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas", {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    readonly_fields = ["date_joined", "last_login", "updated_at"]
