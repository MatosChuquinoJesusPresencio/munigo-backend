from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, BlacklistedToken
from users.serializers import RegisterSerializer, LoginSerializer


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
