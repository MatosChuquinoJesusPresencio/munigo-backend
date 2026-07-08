from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Record, RecordStatus, RiskLevel
from .serializers import (
    RecordCreateSerializer,
    RecordUpdateSerializer,
    RecordSerializer,
    RecordListSerializer,
    RiskClassificationSerializer,
    RiskClassificationResultSerializer,
    DocumentValidationSerializer,
    RiskReclassificationSerializer,
    RecordEvaluationSerializer,
)
from .services import tramite_service
from citizens.models import Citizen
from attachments.models import Attachment
from attachments.serializers import AttachmentListSerializer
from employees.models import Employee


def _get_citizen_or_error(user):
    try:
        return Citizen.objects.get(user=user)
    except Citizen.DoesNotExist:
        return None


def _get_record_or_error(record_id, citizen):
    try:
        record = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return None
    if record.citizen_id != citizen.id:
        return None
    return record


@api_view(['POST'])
def create_record(request):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden crear trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = RecordCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    risk_level = tramite_service.clasificar_riesgo(
        data['business_type'], data['premises_size']
    )

    record = Record.objects.create(
        citizen=citizen,
        procedure_type=data['procedure_type'],
        risk_level=risk_level,
        tracking_code=tramite_service.generar_codigo(),
        business_type=data['business_type'],
        premises_size=data['premises_size'],
        premises_address=data.get('premises_address', ''),
        zone=data.get('zone', ''),
        status=RecordStatus.DRAFT,
    )

    result = RecordSerializer(record)
    return Response(result.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_my_records(request):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden ver sus trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    records = Record.objects.filter(citizen=citizen).order_by('-created_at')
    serializer = RecordListSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT'])
def record_detail_update(request, pk):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden acceder a trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    record = _get_record_or_error(pk, citizen)
    if not record:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = RecordSerializer(record)
        return Response(serializer.data)

    if record.status != RecordStatus.DRAFT:
        return Response(
            {"detail": "Solo se pueden editar expedientes en estado BORRADOR"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RecordUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    for field, value in data.items():
        setattr(record, field, value)

    if 'business_type' in data or 'premises_size' in data:
        record.risk_level = tramite_service.clasificar_riesgo(
            record.business_type, record.premises_size
        )

    record.save()

    result = RecordSerializer(record)
    return Response(result.data)


@api_view(['POST'])
def submit_record(request, pk):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden enviar trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    record = _get_record_or_error(pk, citizen)
    if not record:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.status != RecordStatus.DRAFT:
        return Response(
            {"detail": "Solo se pueden enviar expedientes en estado BORRADOR"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not record.attachment_set.exists():
        return Response(
            {"detail": "Debe subir al menos un documento antes de enviar"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    record.status = RecordStatus.PENDING_REVIEW
    record.save()

    from notifications.services import notificar_expediente_enviado
    notificar_expediente_enviado(citizen, record)

    result = RecordSerializer(record)
    return Response(result.data)


@api_view(['POST'])
def resubmit_record(request, pk):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden reenviar trámites"},
            status=status.HTTP_403_FORBIDDEN,
        )

    record = _get_record_or_error(pk, citizen)
    if not record:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.status != RecordStatus.OBSERVED:
        return Response(
            {"detail": "Solo se pueden reenviar expedientes en estado OBSERVADO"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not record.attachment_set.exists():
        return Response(
            {"detail": "Debe subir al menos un documento antes de reenviar"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    record.attachment_set.filter(
        validation_status='OBSERVADO'
    ).update(validation_status='PENDIENTE', observations='')

    record.status = RecordStatus.PENDING_REVIEW
    record.save()

    from notifications.services import notificar_expediente_enviado
    notificar_expediente_enviado(citizen, record)

    result = RecordSerializer(record)
    return Response(result.data)


@api_view(['GET'])
def list_pending_review(request):
    role = request.user.role
    if role not in ('FUNCIONARIO', 'GERENTE'):
        return Response(
            {"detail": "No tiene permisos para ver esta lista"},
            status=status.HTTP_403_FORBIDDEN,
        )

    records = Record.objects.filter(
        status=RecordStatus.PENDING_REVIEW
    ).order_by('created_at')

    serializer = RecordListSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def classify_risk(request):
    serializer = RiskClassificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    risk_level = tramite_service.clasificar_riesgo(
        data['business_type'], data['premises_size']
    )
    requires_inspection = tramite_service.requiere_inspeccion(risk_level)
    motive = tramite_service.get_risk_motive(risk_level)

    result = RiskClassificationResultSerializer({
        'risk_level': risk_level,
        'requires_inspection': requires_inspection,
        'motive': motive,
    })
    return Response(result.data)


def _get_funcionario_or_error(user):
    if user.role in ('FUNCIONARIO', 'GERENTE'):
        try:
            return Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            if user.role == 'GERENTE':
                return user
    return None


def _puede_revisar(record, employee):
    role = employee.user.role if hasattr(employee, 'user') else employee.role
    if role == 'GERENTE':
        return True
    if record.risk_level == RiskLevel.HIGH and role != 'GERENTE':
        return False
    return True


@api_view(['GET'])
def review_record_detail(request, pk):
    employee = _get_funcionario_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "No tiene permisos de funcionario"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not _puede_revisar(record, employee):
        return Response(
            {"detail": "No tiene permisos para revisar expedientes de alto riesgo"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = RecordEvaluationSerializer(record)
    return Response(serializer.data)


@api_view(['GET'])
def review_record_documents(request, pk):
    employee = _get_funcionario_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "No tiene permisos de funcionario"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not _puede_revisar(record, employee):
        return Response(
            {"detail": "No tiene permisos para revisar expedientes de alto riesgo"},
            status=status.HTTP_403_FORBIDDEN,
        )

    attachments = record.attachment_set.all().order_by('uploaded_at')
    serializer = AttachmentListSerializer(attachments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def validate_document(request):
    employee = _get_funcionario_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "No tiene permisos de funcionario"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = DocumentValidationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        attachment = Attachment.objects.get(id=data['document_id'])
    except Attachment.DoesNotExist:
        return Response(
            {"detail": "Documento no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    record = attachment.record
    if not _puede_revisar(record, employee):
        return Response(
            {"detail": "No tiene permisos para validar documentos de este expediente"},
            status=status.HTTP_403_FORBIDDEN,
        )

    attachment.validation_status = data['validation_status']
    attachment.observations = data.get('observations', '')
    attachment.save()

    if data['validation_status'] == 'OBSERVADO':
        from notifications.services import notificar_documento_observado
        notificar_documento_observado(
            record.citizen,
            attachment.filename,
            data.get('observations', ''),
            record,
        )

    return Response({
        'id': attachment.id,
        'filename': attachment.filename,
        'validation_status': attachment.validation_status,
        'observations': attachment.observations,
    })


@api_view(['POST'])
def finalize_review(request, pk):
    employee = _get_funcionario_or_error(request.user)
    if not employee:
        return Response(
            {"detail": "No tiene permisos de funcionario"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if record.status != RecordStatus.PENDING_REVIEW:
        return Response(
            {"detail": "El expediente no está en estado PENDIENTE_REVISION"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not _puede_revisar(record, employee):
        return Response(
            {"detail": "No tiene permisos para revisar expedientes de alto riesgo"},
            status=status.HTTP_403_FORBIDDEN,
        )

    attachments = record.attachment_set.all()

    if attachments.filter(validation_status='OBSERVADO').exists():
        record.status = RecordStatus.OBSERVED
        from notifications.services import notificar_expediente_observado
        notificar_expediente_observado(record.citizen, record)
    elif not attachments.filter(validation_status='APROBADO').count() == attachments.count():
        return Response(
            {"detail": "No se puede finalizar la revisión hasta que todos los documentos estén validados"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif record.risk_level == RiskLevel.HIGH:
        record.status = RecordStatus.PENDING_INSPECTION
    else:
        record.status = RecordStatus.DOCUMENTS_APPROVED

    record.save()

    result = RecordSerializer(record)
    return Response(result.data)


@api_view(['POST', 'PUT'])
def reclassify_risk(request, pk):
    if request.user.role != 'GERENTE':
        return Response(
            {"detail": "Solo los gerentes pueden reclasificar riesgo"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=pk)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = RiskReclassificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    record.risk_level = serializer.validated_data['risk_level']
    record.save()

    result = RecordSerializer(record)
    return Response(result.data)
