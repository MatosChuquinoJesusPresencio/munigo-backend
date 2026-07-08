from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer
from users.models import Role


@api_view(['GET'])
def employee_profile(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response(
            {"detail": "Perfil de empleado no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inspector_list(request):
    inspectors = Employee.objects.filter(user__role=Role.INSPECTOR)
    serializer = EmployeeSerializer(inspectors, many=True)
    return Response(serializer.data)
