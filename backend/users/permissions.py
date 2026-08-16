"""Permission classes for the users app."""

from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """Allow admins, or a user retrieving their own record."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requester is staff or the object is their own record."""
        return request.user.is_staff or obj == request.user
