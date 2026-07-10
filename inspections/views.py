from rest_framework import viewsets, permissions

from inspections.models import Inspection
from inspections.serializers import InspectionSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InspectionSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            employee = user.citizen.employee
            if employee.position == "INSPECTOR":
                return Inspection.objects.filter(appointment__inspector=employee)
            return Inspection.objects.filter(appointment__case_file__citizen__user=user)
        except AttributeError:
            return Inspection.objects.filter(appointment__case_file__citizen__user=user)
