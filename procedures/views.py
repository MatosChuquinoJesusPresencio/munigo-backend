from rest_framework import viewsets, permissions

from procedures.models import CaseFile, Requirement
from procedures.serializers import CaseFileSerializer, RequirementSerializer


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
    serializer_class = CaseFileSerializer

    def get_queryset(self):
        return CaseFile.objects.filter(citizen__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
