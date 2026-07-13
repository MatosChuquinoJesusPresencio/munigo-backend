from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from users.models import User, Employee, BlacklistedToken
from users.serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    EmployeeSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer,
)


class IsGerente(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.citizen.employee.position == "GERENTE"
        except AttributeError:
            return False


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            request.user.citizen.employee
            return True
        except AttributeError:
            return False


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.none()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenViewBase):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Token refresh es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token)
        except Exception:
            return Response(
                {"detail": "Token refresh inválido o expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        BlacklistedToken.objects.get_or_create(token=refresh_token)
        return Response(
            {"detail": "Sesión cerrada exitosamente."},
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsGerente]

    def get_queryset(self):
        qs = Employee.objects.select_related("citizen__user")
        position = self.request.query_params.get("position")
        if position:
            qs = qs.filter(position=position)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeCreateSerializer
        if self.action in ("update", "partial_update"):
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        user = instance.citizen.user
        instance.delete()
        user.delete()
