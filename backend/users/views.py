"""Views for the users app.

Defines the authentication (login) view and the CRUD views for the User model
(list, retrieve, create, update, delete).
"""

from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsSelfOrAdmin
from .serializers import UserSerializer, LoginSerializer


class UserNotFoundMixin:
    """Raise a Portuguese not-found message instead of DRF's default detail."""

    def get_object(self):
        """Return the user or raise NotFound with the project's standard message."""
        try:
            return super().get_object()
        except Http404 as exc:
            raise NotFound("Usuário não encontrado.") from exc


class LoginView(APIView):
    """Authenticate a user by email/password and return JWT tokens (public)."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate the credentials and return JWT tokens when they are valid.

        A malformed email is treated the same as a wrong password: both fall
        through to the generic 401 below instead of ``raise_exception``,
        which would otherwise expose a field-specific format error and reveal
        that the email (rather than the password) was the problem.
        """
        serializer = LoginSerializer(data=request.data)
        user = None
        if serializer.is_valid():
            user = authenticate(request, **serializer.validated_data)

        if user is None:
            return Response(
                {"email": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": str(user.id),
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    """List all users, newest first (admin only)."""

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(UserNotFoundMixin, generics.RetrieveAPIView):
    """Retrieve a single user (own record, or any record for an admin)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]


class UserCreateView(generics.CreateAPIView):
    """Register a new user (public)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserUpdateView(UserNotFoundMixin, generics.UpdateAPIView):
    """Update an existing user (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDeleteView(UserNotFoundMixin, generics.DestroyAPIView):
    """Delete a user (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
