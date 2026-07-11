from rest_framework import viewsets, permissions

from procedures.models import CaseFile, Requirement, Appointment
from procedures.serializers import (
    CaseFileListSerializer,
    CaseFileDetailSerializer,
    RequirementSerializer,
    AppointmentSerializer,
)


class RequirementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RequirementSerializer

    def get_queryset(self):
        qs = Requirement.objects.all()
        procedure_type = self.request.query_params.get("procedure_type")
        if procedure_type:
            qs = qs.filter(procedure_type=procedure_type)
        return qs


class CaseFileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return CaseFileListSerializer
        return CaseFileDetailSerializer

    def get_queryset(self):
        return CaseFile.objects.select_related('establishment', 'establishment__company').filter(citizen__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(citizen=self.request.user.citizen)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.select_related('case_file', 'inspector__citizen__user').filter(case_file__citizen__user=self.request.user)
