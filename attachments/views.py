import os
import uuid
from datetime import datetime

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Attachment
from .serializers import AttachmentListSerializer
from records.models import Record, RecordStatus
from citizens.models import Citizen

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}


def _get_citizen_or_error(user):
    try:
        return Citizen.objects.get(user=user)
    except Citizen.DoesNotExist:
        return None


@api_view(['GET', 'POST'])
def record_documents(request, pk):
    citizen = _get_citizen_or_error(request.user)
    if not citizen:
        return Response(
            {"detail": "Solo ciudadanos pueden acceder a documentos"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        record = Record.objects.get(id=pk, citizen=citizen)
    except Record.DoesNotExist:
        return Response(
            {"detail": "Expediente no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        attachments = record.attachment_set.all().order_by('-uploaded_at')
        serializer = AttachmentListSerializer(attachments, many=True)
        return Response(serializer.data)

    if record.status not in (RecordStatus.DRAFT, RecordStatus.OBSERVED):
        return Response(
            {"detail": "Solo se pueden subir documentos a expedientes en estado BORRADOR u OBSERVADO"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if 'file' not in request.FILES:
        return Response(
            {"detail": "Debe enviar un archivo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    uploaded = request.FILES['file']

    if uploaded.size > MAX_UPLOAD_SIZE:
        return Response(
            {"detail": f"El archivo excede el tamaño máximo de 10 MB"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return Response(
            {"detail": f"Tipo de archivo no permitido. Extensiones: {', '.join(ALLOWED_EXTENSIONS)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    requirement_id = request.POST.get('requirement')

    unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    relative_path = os.path.join('records', str(record.id), unique_name)
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

    with open(absolute_path, 'wb+') as f:
        for chunk in uploaded.chunks():
            f.write(chunk)

    if requirement_id:
        from requirements.models import Requirement
        try:
            requirement = Requirement.objects.get(id=requirement_id)
        except Requirement.DoesNotExist:
            requirement = None
    else:
        requirement = None

    attachment = Attachment.objects.create(
        record=record,
        requirement=requirement,
        filename=uploaded.name,
        file_path=relative_path,
        validation_status='PENDIENTE',
    )

    return Response({
        'id': attachment.id,
        'filename': attachment.filename,
        'file_path': attachment.file_path,
        'validation_status': attachment.validation_status,
        'message': 'Documento subido exitosamente',
    }, status=status.HTTP_201_CREATED)
