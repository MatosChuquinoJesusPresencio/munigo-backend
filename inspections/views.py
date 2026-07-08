import os
from datetime import datetime
from uuid import uuid4

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Inspection, InspectionResult
from .serializers import (
    AssignInspectionSerializer,
    InspectionResultSerializer,
    InspectionSerializer,
    RouteSheetItemSerializer,
    RouteSheetSerializer,
)
from records.models import Record, RecordStatus
from employees.models import Employee
from citizens.models import Citizen
from appointments.models import Appointment


def _get_employee_or_error(user):
    try:
        return Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return None


def _get_citizen_or_error(user):
    try:
        return Citizen.objects.get(user=user)
    except Citizen.DoesNotExist:
        return None


def _handle_photo(file):
    if not file or not file.name:
        return ""
    ext = os.path.splitext(file.name)[1] or ".jpg"
    filename = f"inspections/{uuid4().hex}{ext}"
    path = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return filename


@api_view(["POST"])
def assign_inspection(request):
    role = request.user.role
    if role not in ("FUNCIONARIO", "GERENTE"):
        return Response(
            {"detail": "No tiene permisos para asignar inspecciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AssignInspectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        record = Record.objects.get(id=data["record_id"])
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.status != RecordStatus.PENDING_INSPECTION:
        return Response(
            {"detail": "Solo se pueden asignar inspecciones a expedientes en PENDIENTE_INSPECCION"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        inspector = Employee.objects.get(id=data["inspector_id"])
    except Employee.DoesNotExist:
        return Response(
            {"detail": "Inspector no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if inspector.user.role != "INSPECTOR":
        return Response(
            {"detail": "El empleado seleccionado no tiene rol de INSPECTOR"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    inspection = Inspection.objects.create(
        record=record,
        inspector=inspector,
        result=InspectionResult.PENDING,
        comments="",
        scheduled_date=data.get("scheduled_date"),
    )

    result = InspectionSerializer(inspection)
    return Response(result.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def route_sheet(request):
    if request.user.role != "INSPECTOR":
        return Response(
            {"detail": "Solo inspectores pueden ver su hoja de ruta"},
            status=status.HTTP_403_FORBIDDEN,
        )

    employee = _get_employee_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "Perfil de empleado no encontrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    date_str = request.query_params.get("date")
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        date = datetime.now().date()

    inspections = Inspection.objects.filter(
        inspector=employee,
        result=InspectionResult.PENDING,
        scheduled_date__date=date,
    ).order_by("scheduled_date")

    items = []
    for ins in inspections.select_related("record"):
        items.append({
            "inspection_id": ins.id,
            "record_id": ins.record.id,
            "tracking_code": ins.record.tracking_code,
            "address": ins.record.premises_address,
            "zone": ins.record.zone,
            "business_type": ins.record.business_type,
            "scheduled_date": ins.scheduled_date,
        })

    data = RouteSheetSerializer({
        "inspector_id": employee.id,
        "inspector_name": f"{employee.first_name} {employee.last_name}",
        "date": date,
        "inspections": items,
    }).data

    return Response(data)


@api_view(["GET"])
def my_inspections(request):
    if request.user.role != "INSPECTOR":
        return Response(
            {"detail": "Solo inspectores pueden ver sus inspecciones"},
            status=status.HTTP_403_FORBIDDEN,
        )

    employee = _get_employee_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "Perfil de empleado no encontrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    inspections = Inspection.objects.filter(inspector=employee).order_by("-created_at")
    serializer = InspectionSerializer(inspections, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def inspection_detail(request, pk):
    if request.user.role != "INSPECTOR":
        return Response(
            {"detail": "Solo inspectores pueden ver detalles de inspección"},
            status=status.HTTP_403_FORBIDDEN,
        )

    employee = _get_employee_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "Perfil de empleado no encontrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        inspection = Inspection.objects.get(id=pk)
    except Inspection.DoesNotExist:
        return Response(
            {"detail": "Inspección no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if inspection.inspector_id != employee.id:
        return Response(
            {"detail": "No tiene permisos para ver esta inspección"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = InspectionSerializer(inspection)
    return Response(serializer.data)


@api_view(["POST"])
def register_result(request, pk):
    if request.user.role != "INSPECTOR":
        return Response(
            {"detail": "Solo inspectores pueden registrar resultados"},
            status=status.HTTP_403_FORBIDDEN,
        )

    employee = _get_employee_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "Perfil de empleado no encontrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        inspection = Inspection.objects.get(id=pk)
    except Inspection.DoesNotExist:
        return Response(
            {"detail": "Inspección no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if inspection.inspector_id != employee.id:
        return Response(
            {"detail": "No tiene permisos para registrar el resultado de esta inspección"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if inspection.result != InspectionResult.PENDING:
        return Response(
            {"detail": "Esta inspección ya tiene un resultado registrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = InspectionResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    photo = request.FILES.get("photo")
    photo_path = _handle_photo(photo)

    inspection.result = data["result"]
    inspection.comments = data.get("comments", "")
    inspection.photo_path = photo_path
    inspection.execution_date = datetime.now()
    inspection.save()

    if data["result"] == InspectionResult.APPROVED:
        inspection.record.status = RecordStatus.APPROVED
    else:
        inspection.record.status = RecordStatus.REJECTED

    inspection.record.save()

    from notifications.services import notificar_expediente_aprobado, notificar_expediente_rechazado
    if data["result"] == InspectionResult.APPROVED:
        notificar_expediente_aprobado(inspection.record.citizen, inspection.record)
    else:
        notificar_expediente_rechazado(
            inspection.record.citizen,
            inspection.record,
            data.get("comments", ""),
        )

    result = InspectionSerializer(inspection)
    return Response(result.data)


@api_view(["GET"])
def inspections_by_record(request, record_id):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden ver inspecciones de sus trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.citizen_id != citizen.id:
        return Response(
            {"detail": "No tiene permisos para ver inspecciones de este expediente"},
            status=status.HTTP_403_FORBIDDEN,
        )

    inspections = Inspection.objects.filter(record=record).order_by("-created_at")
    serializer = InspectionSerializer(inspections, many=True)
    return Response(serializer.data)
