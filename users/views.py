from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User, Role
from citizens.models import Citizen


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = serializer.validated_data

    user = User.objects.create_user(
        username=data['email'],
        email=data['email'],
        password=data['password'],
        role=Role.CITIZEN,
    )

    Citizen.objects.create(
        user=user,
        document_type=data['document_type'],
        document_number=data['document_number'],
        legal_name=data['legal_name'],
        phone=data.get('phone', ''),
        address=data.get('address', ''),
    )

    token = AccessToken.for_user(user)

    return Response({
        'access_token': str(token),
        'token_type': 'bearer',
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = serializer.validated_data

    user = data['user']
    token = AccessToken.for_user(user)

    response = Response({
        'access_token': str(token),
        'token_type': 'bearer',
        'user': UserSerializer(user).data,
    })

    response.set_cookie(
        key='access_token',
        value=str(token),
        httponly=True,
        samesite='Lax',
        max_age=86400,
    )

    return response


@api_view(['GET'])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    response = Response({'message': 'Sesión cerrada correctamente'})
    response.delete_cookie('access_token')
    return response
