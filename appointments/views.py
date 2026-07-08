from datetime import time, datetime, timedelta, date

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Appointment, AppointmentStatus
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
)
from records.models import Record, RecordStatus
from citizens.models import Citizen
from employees.models import Employee


HORA_INICIO = time(8, 0)
HORA_FIN = time(17, 0)
DURACION = 60


def _generar_horarios():
    slots = []
    actual = datetime(2000, 1, 1, HORA_INICIO.hour, 0)
    fin = datetime(2000, 1, 1, HORA_FIN.hour, 0)
    while actual < fin:
        fin_slot = actual + timedelta(minutes=DURACION)
        if fin_slot > fin:
            break
        slots.append({'start_time': actual.time(), 'end_time': fin_slot.time()})
        actual = fin_slot
    return slots


@api_view(['GET'])
def availability(request):
    date_str = request.query_params.get('date')
    if not date_str:
        return Response(
            {"detail": "Debe especificar una fecha (YYYY-MM-DD)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        fecha = date.fromisoformat(date_str)
    except ValueError:
        return Response(
            {"detail": "Formato de fecha inválido. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if fecha.weekday() >= 5:
        return Response([])

    todos_slots = _generar_horarios()

    ocupados = set()
    citas = Appointment.objects.filter(date=fecha, status=AppointmentStatus.SCHEDULED)
    for c in citas:
        ocupados.add((c.start_time, c.end_time))

    disponibles = [
        s for s in todos_slots
        if (s['start_time'], s['end_time']) not in ocupados
    ]

    return Response(disponibles)


@api_view(['POST'])
def schedule_appointment(request):
    try:
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        return Response(
            {"detail": "Solo ciudadanos pueden programar citas"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AppointmentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        record = Record.objects.get(id=data['record_id'], citizen=citizen)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.status != RecordStatus.PENDING_INSPECTION:
        return Response(
            {"detail": "Solo se pueden programar citas para expedientes en PENDIENTE_INSPECCION"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    fecha = data['date']
    if fecha.weekday() >= 5:
        return Response(
            {"detail": "Solo se pueden programar citas en días hábiles (Lunes-Viernes)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check availability
    ocupados = Appointment.objects.filter(
        date=fecha,
        start_time=data['start_time'],
        end_time=data['end_time'],
        status=AppointmentStatus.SCHEDULED,
    ).exists()
    if ocupados:
        return Response(
            {"detail": "El horario solicitado no está disponible"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    officer = None
    officer_id = data.get('officer_id')
    if officer_id:
        try:
            officer = Employee.objects.get(id=officer_id)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Funcionario no encontrado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    appointment = Appointment.objects.create(
        record=record,
        officer=officer,
        date=fecha,
        start_time=data['start_time'],
        end_time=data['end_time'],
        status=AppointmentStatus.SCHEDULED,
    )

    from notifications.services import notificar_cita_programada
    notificar_cita_programada(
        citizen,
        str(appointment.date),
        str(appointment.start_time),
        record,
    )

    result = AppointmentSerializer(appointment)
    return Response(result.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def my_appointments(request):
    try:
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        return Response(
            {"detail": "Solo ciudadanos pueden ver sus citas"},
            status=status.HTTP_403_FORBIDDEN,
        )

    appointments = Appointment.objects.filter(
        record__citizen=citizen
    ).order_by('-date', '-start_time')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def officer_appointments(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response(
            {"detail": "No tiene permisos de funcionario"},
            status=status.HTTP_403_FORBIDDEN,
        )

    appointments = Appointment.objects.filter(
        officer=employee,
        status=AppointmentStatus.SCHEDULED,
    ).order_by('date', 'start_time')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET', 'DELETE'])
def appointment_detail(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    except Appointment.DoesNotExist:
        return Response(
            {"detail": "Cita no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    is_owner = appointment.record.citizen.user_id == request.user.id
    is_officer = appointment.officer and appointment.officer.user_id == request.user.id
    is_staff = request.user.role in ('FUNCIONARIO', 'GERENTE')

    if not (is_owner or is_officer or is_staff):
        return Response(
            {"detail": "No tiene permisos para acceder a esta cita"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    if not is_owner:
        return Response(
            {"detail": "Solo el ciudadano puede cancelar la cita"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if appointment.status != AppointmentStatus.SCHEDULED:
        return Response(
            {"detail": "Solo se pueden cancelar citas programadas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.status = AppointmentStatus.CANCELED
    appointment.save()

    from notifications.services import notificar_cita_cancelada
    notificar_cita_cancelada(
        appointment.record.citizen,
        str(appointment.date),
        str(appointment.start_time),
        appointment.record,
    )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)
