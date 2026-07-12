from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from users.models import User, Citizen, Employee, Role, DocumentType


def generate_username(first_name: str, last_name: str, document_number: str) -> str:
    return document_number


class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        exclude = ["user"]


class EmployeeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="citizen.user.first_name", read_only=True)
    last_name = serializers.CharField(source="citizen.user.last_name", read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "position", "area", "first_name", "last_name"]


class UserSerializer(serializers.ModelSerializer):
    citizen = CitizenSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "citizen", "employee"]


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    document_type = serializers.ChoiceField(choices=DocumentType.choices)
    document_number = serializers.CharField(max_length=22)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_document_number(self, value):
        if Citizen.objects.filter(document_number=value).exists():
            raise serializers.ValidationError("Este documento ya está registrado.")
        return value

    def create(self, validated_data):
        username = generate_username(
            validated_data["first_name"],
            validated_data["last_name"],
            validated_data["document_number"],
        )

        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            password=validated_data["password"],
            role=Role.CITIZEN,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Citizen.objects.create(
            user=user,
            document_type=validated_data["document_type"],
            document_number=validated_data["document_number"],
        )

        return user

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class LoginSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentType.choices)
    document_number = serializers.CharField(max_length=22)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get("request"),
            document_type=data["document_type"],
            document_number=data["document_number"],
            password=data["password"],
        )
        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
