from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from organizations.models import Company, Establishment
from organizations.serializers import (
    CompanySerializer,
    CompanyListSerializer,
    EstablishmentSerializer,
    AddCitizenSerializer,
)
from users.models import Citizen


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        return CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(citizens__user=self.request.user)

    def perform_create(self, serializer):
        company = serializer.save()
        citizen = Citizen.objects.get(user=self.request.user)
        company.citizens.add(citizen)

    @action(detail=True, methods=["post"])
    def add_citizen(self, request, pk=None):
        company = self.get_object()
        serializer = AddCitizenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        citizen = Citizen.objects.get(id=serializer.validated_data["citizen_id"])
        if company.citizens.filter(id=citizen.id).exists():
            return Response(
                {"detail": "El ciudadano ya pertenece a esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company.citizens.add(citizen)
        return Response(
            {"detail": "Ciudadano agregado a la empresa."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def remove_citizen(self, request, pk=None):
        company = self.get_object()
        serializer = AddCitizenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        citizen = Citizen.objects.get(id=serializer.validated_data["citizen_id"])
        if not company.citizens.filter(id=citizen.id).exists():
            return Response(
                {"detail": "El ciudadano no pertenece a esta empresa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company.citizens.remove(citizen)
        return Response(
            {"detail": "Ciudadano removido de la empresa."},
            status=status.HTTP_200_OK,
        )


class EstablishmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EstablishmentSerializer

    def get_queryset(self):
        return Establishment.objects.filter(company__citizens__user=self.request.user)

    def perform_create(self, serializer):
        company = serializer.validated_data["company"]
        citizen = Citizen.objects.get(user=self.request.user)
        if not company.citizens.filter(id=citizen.id).exists():
            raise serializers.ValidationError(
                {"company": "No eres ciudadano de esta empresa."}
            )
        serializer.save()
