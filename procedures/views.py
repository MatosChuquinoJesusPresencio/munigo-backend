from rest_framework import viewsets, permissions

from procedures.models import CaseFile
from procedures.serializers import CaseFileSerializer


class CaseFileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CaseFileSerializer

    def get_queryset(self):
        return CaseFile.objects.filter(citizen__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
