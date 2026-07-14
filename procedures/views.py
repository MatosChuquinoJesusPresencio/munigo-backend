from rest_framework import viewsets, permissions, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from procedures.models import (
    CaseFile, CaseFileStatus, Requirement, Appointment, AppointmentStatus,
    ProcedureRequirement, AttachedDocument, ValidationStatus,
)
from users.models import Position
from procedures.serializers import (
    CaseFileListSerializer,
    CaseFileDetailSerializer,
    RequirementSerializer,
    AppointmentSerializer,
    ProcedureRequirementSerializer,
    AttachedDocumentSerializer,
    AttachedDocumentValidateSerializer,
    AssignInspectorSerializer,
    CaseFileSetStatusSerializer,
)


def _is_employee(user):
    try:
        user.citizen.employee
        return True
    except AttributeError:
        return False


from datetime import date


def _cancel_past_appointments():
    from django.utils import timezone
    today = timezone.localdate()
    past_active = Appointment.objects.filter(
        scheduled_date__lt=today,
        status__in=[
            AppointmentStatus.PENDING_CONFIRMATION,
            AppointmentStatus.PENDING_RESCHEDULE,
        ],
    ).select_related('case_file')

    for appointment in past_active:
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancel_reason = "Cita vencida: la fecha programada ya pasó."
        appointment.save(update_fields=["status", "cancel_reason"])
        case_file = appointment.case_file
        if case_file.status == CaseFileStatus.PENDING_INSPECTION:
            case_file.status = CaseFileStatus.DOCUMENTS_APPROVED
            case_file.save(update_fields=["status"])


class RequirementViewSet(viewsets.ModelViewSet):
    serializer_class = RequirementSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsGerente()]

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
        user = self.request.user
        if hasattr(user, 'citizen') and hasattr(user.citizen, 'employee'):
            return CaseFile.objects.select_related(
                'establishment', 'establishment__company', 'citizen__user'
            ).prefetch_related('appointments').all()
        return CaseFile.objects.select_related(
            'establishment', 'establishment__company'
        ).prefetch_related('appointments').filter(citizen__user=user)

    def perform_create(self, serializer):
        serializer.save(citizen=self.request.user.citizen)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        case_file = self.get_object()

        if case_file.status != CaseFileStatus.DRAFT:
            return Response(
                {"detail": "Solo se pueden enviar expedientes en borrador."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unfulfilled = ProcedureRequirement.objects.filter(
            case_file=case_file,
            requirement__is_required=True,
            fulfilled=False,
        )
        if unfulfilled.exists():
            names = list(unfulfilled.values_list("requirement__name", flat=True))
            return Response(
                {"detail": f"Faltan requisitos obligatorios: {', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case_file.status = CaseFileStatus.PENDING_REVIEW
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Trámite enviado",
            message=f"Tu trámite {case_file.tracking_code} fue enviado exitosamente y está pendiente de revisión.",
        )

        return Response(CaseFileDetailSerializer(case_file).data)

    @action(detail=False, methods=["get"], url_path="pending-review")
    def pending_review(self, request):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        qs = CaseFile.objects.select_related(
            "establishment", "establishment__company", "citizen__user"
        ).filter(status=CaseFileStatus.PENDING_REVIEW)
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        qs = CaseFile.objects.select_related(
            "establishment", "establishment__company", "citizen__user"
        ).exclude(status=CaseFileStatus.PENDING_REVIEW).exclude(status=CaseFileStatus.DRAFT)
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

        from django.db.models import Count

        total = CaseFile.objects.count()
        by_status = dict(
            CaseFile.objects.values_list('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        by_procedure_type = dict(
            CaseFile.objects.values_list('procedure_type')
            .annotate(count=Count('id'))
            .values_list('procedure_type', 'count')
        )
        return Response({
            "total": total,
            "by_status": by_status,
            "by_procedure_type": by_procedure_type,
        })

    @action(detail=True, methods=["post"], url_path="approve-documents")
    def approve_documents(self, request, pk=None):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        case_file = self.get_object()

        if case_file.status != CaseFileStatus.PENDING_REVIEW:
            return Response(
                {"detail": "Solo se pueden aprobar documentos de expedientes pendientes de revisión."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        required_unapproved = ProcedureRequirement.objects.filter(
            case_file=case_file,
            requirement__is_required=True,
        ).exclude(
            documents__validation_status=ValidationStatus.APPROVED
        )

        if required_unapproved.exists():
            names = list(required_unapproved.values_list("requirement__name", flat=True))
            return Response(
                {"detail": f"Requisitos obligatorios sin aprobar: {', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case_file.status = CaseFileStatus.DOCUMENTS_APPROVED
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Documentos aprobados",
            message=f"Los documentos de tu trámite {case_file.tracking_code} fueron aprobados.",
        )

        return Response(CaseFileDetailSerializer(case_file).data)

    @action(detail=True, methods=["post"], url_path="assign-inspector")
    def assign_inspector(self, request, pk=None):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        case_file = self.get_object()

        if case_file.status != CaseFileStatus.DOCUMENTS_APPROVED:
            return Response(
                {"detail": "Solo se puede asignar inspector a expedientes con documentos aprobados."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignInspectorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from users.models import Employee
        inspector = Employee.objects.get(id=data["inspector_id"])

        user = request.user
        try:
            employee = request.user.citizen.employee
        except AttributeError:
            return Response(
                {"detail": "El usuario no es un empleado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if employee.position not in (Position.OFFICIAL, Position.MANAGER):
            return Response(
                {"detail": "Solo un funcionario o gerente puede asignar inspectores."},
                status=status.HTTP_403_FORBIDDEN,
            )

        Appointment.objects.create(
            case_file=case_file,
            created_by=employee,
            inspector=inspector,
            scheduled_date=data["scheduled_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            notes=data.get("notes", ""),
        )

        case_file.status = CaseFileStatus.PENDING_INSPECTION
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Cita pendiente de confirmación",
            message=f"Se programó una inspección para tu trámite {case_file.tracking_code}. Confirma o rechaza la cita desde 'Mis Citas'.",
        )

        return Response(CaseFileDetailSerializer(case_file).data)

    @action(detail=True, methods=["get"], url_path="download-license")
    def download_license(self, request, pk=None):
        case_file = self.get_object()

        if case_file.status != CaseFileStatus.APPROVED:
            return Response(
                {"detail": "Solo se puede descargar la licencia de expedientes aprobados."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if case_file.procedure_type != "LICENCIA_DE_FUNCIONAMIENTO":
            return Response(
                {"detail": "La licencia solo esta disponible para Licencias de Funcionamiento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from procedures.pdf_generator import generate_license_pdf
        pdf_bytes = generate_license_pdf(case_file)

        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        filename = f"licencia_{case_file.tracking_code}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        if not _is_employee(request.user):
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        try:
            case_file = self.get_object()

            serializer = CaseFileSetStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_status = serializer.validated_data["status"]

            allowed_transitions = {
                CaseFileStatus.APPROVED: [CaseFileStatus.PENDING_INSPECTION],
                CaseFileStatus.OBSERVED: [CaseFileStatus.PENDING_INSPECTION, CaseFileStatus.PENDING_REVIEW],
                CaseFileStatus.REJECTED: [CaseFileStatus.PENDING_INSPECTION, CaseFileStatus.PENDING_REVIEW],
            }

            allowed_from_pending = {
                CaseFileStatus.APPROVED: CaseFileStatus.PENDING_REVIEW,
                CaseFileStatus.REJECTED: CaseFileStatus.PENDING_REVIEW,
            }

            if case_file.status == CaseFileStatus.PENDING_REVIEW:
                if new_status not in allowed_from_pending:
                    return Response(
                        {"detail": f"No se puede cambiar de Pendiente de revisión a {new_status}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif case_file.status not in allowed_transitions.get(new_status, []):
                return Response(
                    {"detail": f"No se puede cambiar de {case_file.get_status_display()} a {new_status}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            case_file.status = new_status
            observations = serializer.validated_data.get("observations", "").strip()
            update_fields = ["status"]
            if observations:
                case_file.observations = observations
                update_fields.append("observations")
            case_file.save(update_fields=update_fields)

            status_labels = {
                CaseFileStatus.APPROVED: "aprobado",
                CaseFileStatus.OBSERVED: "observado",
                CaseFileStatus.REJECTED: "rechazado",
            }

            from notifications.models import Notification
            Notification.objects.create(
                citizen=case_file.citizen,
                case_file=case_file,
                title=f"Trámite {status_labels[new_status]}",
                message=f"Tu trámite {case_file.tracking_code} fue {status_labels[new_status]}.",
            )

            return Response(CaseFileDetailSerializer(case_file).data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

    @action(detail=False, methods=["get"], url_path="my-inspections")
    def my_inspections(self, request):
        try:
            employee = request.user.citizen.employee
        except AttributeError:
            return Response(
                {"detail": "El usuario no es un empleado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        _cancel_past_appointments()

        appointments = Appointment.objects.filter(
            inspector=employee,
            status__in=[
                AppointmentStatus.PENDING_CONFIRMATION,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.PENDING_RESCHEDULE,
            ],
        ).select_related('case_file', 'case_file__establishment', 'case_file__establishment__company')

        case_file_ids = appointments.values_list('case_file_id', flat=True).distinct()
        qs = CaseFile.objects.filter(id__in=case_file_ids).select_related(
            'establishment', 'establishment__company', 'citizen__user'
        )
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="inspection-history")
    def inspection_history(self, request):
        try:
            employee = request.user.citizen.employee
        except AttributeError:
            return Response(
                {"detail": "El usuario no es un empleado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        finished_statuses = [
            CaseFileStatus.APPROVED,
            CaseFileStatus.OBSERVED,
            CaseFileStatus.REJECTED,
        ]
        appointments = Appointment.objects.filter(
            inspector=employee,
            case_file__status__in=finished_statuses,
        ).select_related('case_file')

        case_file_ids = appointments.values_list('case_file_id', flat=True).distinct()
        qs = CaseFile.objects.filter(id__in=case_file_ids).select_related(
            'establishment', 'establishment__company', 'citizen__user'
        )
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="complete-inspection")
    def complete_inspection(self, request, pk=None):
        case_file = self.get_object()

        try:
            employee = request.user.citizen.employee
        except AttributeError:
            return Response(
                {"detail": "El usuario no es un empleado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        appointment = Appointment.objects.filter(
            case_file=case_file,
            inspector=employee,
        ).first()

        if not appointment:
            return Response(
                {"detail": "No tienes una inspección asignada para este expediente."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hasattr(appointment, 'inspection'):
            return Response(
                {"detail": "Esta inspección ya fue completada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment.status != AppointmentStatus.CONFIRMED:
            return Response(
                {"detail": "La cita debe estar confirmada antes de completar la inspección."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from inspections.models import Inspection, InspectionResult
        result = request.data.get("result")
        if result not in dict(InspectionResult.choices):
            return Response(
                {"detail": "El resultado debe ser APROBADO o NO_APROBADO."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = request.data.get("comments", "")
        photo_urls = request.data.get("photo_urls", [])

        Inspection.objects.create(
            appointment=appointment,
            result=result,
            comments=comments,
            photo_urls=photo_urls,
        )

        appointment.status = AppointmentStatus.COMPLETED
        appointment.save(update_fields=["status"])

        if result == InspectionResult.APPROVED:
            case_file.status = CaseFileStatus.APPROVED
            status_label = "aprobado"
        else:
            case_file.status = CaseFileStatus.REJECTED
            status_label = "rechazado"

        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Inspección completada",
            message=f"La inspección de tu trámite {case_file.tracking_code} fue {status_label}.",
        )

        return Response({"detail": f"Inspección completada. Trámite {status_label}."})


class ProcedureRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProcedureRequirementSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'citizen') and hasattr(user.citizen, 'employee'):
            qs = ProcedureRequirement.objects.select_related('requirement').prefetch_related('documents').all()
        else:
            qs = ProcedureRequirement.objects.select_related('requirement').prefetch_related('documents').filter(
                case_file__citizen__user=user
            )
        case_file_id = self.request.query_params.get("case_file")
        if case_file_id:
            qs = qs.filter(case_file_id=case_file_id)
        return qs


class AttachedDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachedDocumentSerializer
    parser_classes = [parsers.JSONParser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'citizen') and hasattr(user.citizen, 'employee'):
            return AttachedDocument.objects.all()
        return AttachedDocument.objects.filter(
            procedure_requirement__case_file__citizen__user=user
        )

    def perform_create(self, serializer):
        doc = serializer.save()
        doc.procedure_requirement.fulfilled = True
        doc.procedure_requirement.save(update_fields=["fulfilled"])

    def perform_destroy(self, instance):
        pr = instance.procedure_requirement
        instance.delete()
        if not pr.documents.exists():
            pr.fulfilled = False
            pr.save(update_fields=["fulfilled"])

    @action(detail=True, methods=["patch"], url_path="validate")
    def validate_document(self, request, pk=None):
        doc = self.get_object()
        serializer = AttachedDocumentValidateSerializer(doc, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AttachedDocumentSerializer(doc).data)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def list(self, request, *args, **kwargs):
        _cancel_past_appointments()
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if _is_employee(user):
            return Appointment.objects.select_related(
                'case_file', 'case_file__establishment',
                'case_file__citizen__user',
                'inspector__citizen__user',
                'created_by__citizen__user',
            ).all()
        return Appointment.objects.select_related(
            'case_file', 'case_file__establishment',
            'inspector__citizen__user',
        ).filter(case_file__citizen__user=user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        user = request.user

        if not hasattr(user, 'citizen'):
            return Response(
                {"detail": "Solo el ciudadano puede confirmar la cita."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if appointment.case_file.citizen.user != user:
            return Response(
                {"detail": "Esta cita no te pertenece."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if appointment.status != AppointmentStatus.PENDING_CONFIRMATION:
            return Response(
                {"detail": "Solo se pueden confirmar citas pendientes de confirmación."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.CONFIRMED
        appointment.save(update_fields=["status"])

        case_file = appointment.case_file
        case_file.status = CaseFileStatus.PENDING_INSPECTION
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Cita confirmada",
            message=f"La inspección para tu trámite {case_file.tracking_code} ha sido confirmada.",
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        user = request.user
        reason = request.data.get("reason", "").strip()

        if not reason:
            return Response(
                {"detail": "El motivo de cancelación es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_citizen = hasattr(user, 'citizen') and appointment.case_file.citizen.user == user
        is_employee = _is_employee(user)

        if not is_citizen and not is_employee:
            return Response(
                {"detail": "No autorizado para cancelar esta cita."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if appointment.status not in (
            AppointmentStatus.PENDING_CONFIRMATION,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.PENDING_RESCHEDULE,
        ):
            return Response(
                {"detail": "No se puede cancelar una cita en este estado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancel_reason = reason
        appointment.save(update_fields=["status", "cancel_reason"])

        case_file = appointment.case_file
        case_file.status = CaseFileStatus.DOCUMENTS_APPROVED
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        if is_citizen:
            notify_to = case_file.citizen
            title = "Cita cancelada por el ciudadano"
            msg = f"El ciudadano canceló la cita del trámite {case_file.tracking_code}. Motivo: {reason}"
        else:
            notify_to = case_file.citizen
            title = "Cita cancelada"
            msg = f"La cita del trámite {case_file.tracking_code} fue cancelada. Motivo: {reason}"

        Notification.objects.create(
            citizen=notify_to,
            case_file=case_file,
            title=title,
            message=msg,
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        user = request.user

        if not hasattr(user, 'citizen') or appointment.case_file.citizen.user != user:
            return Response(
                {"detail": "Solo el ciudadano puede solicitar reprogramación."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if appointment.status != AppointmentStatus.CONFIRMED:
            return Response(
                {"detail": "Solo se pueden reprogramar citas confirmadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_date = request.data.get("new_date")
        new_start = request.data.get("new_start_time")
        new_end = request.data.get("new_end_time")
        reason = request.data.get("reason", "").strip()

        if not all([new_date, new_start, new_end, reason]):
            return Response(
                {"detail": "Fecha, horas y motivo son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.PENDING_RESCHEDULE
        appointment.notes = (
            f"Reprogramación solicitada: {new_date} {new_start}-{new_end}. Motivo: {reason}"
        )
        appointment.save(update_fields=["status", "notes"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=appointment.case_file.citizen,
            case_file=appointment.case_file,
            title="Solicitud de reprogramación",
            message=f"El ciudadano solicitó reprogramar la cita del trámite {appointment.case_file.tracking_code}.",
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="respond-reschedule")
    def respond_reschedule(self, request, pk=None):
        appointment = self.get_object()

        if not _is_employee(request.user):
            return Response(
                {"detail": "Solo un empleado puede responder reprogramaciones."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if appointment.status != AppointmentStatus.PENDING_RESCHEDULE:
            return Response(
                {"detail": "Esta cita no tiene una solicitud de reprogramación pendiente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        accept = request.data.get("accept", False)

        if accept:
            new_date = request.data.get("new_date")
            new_start = request.data.get("new_start_time")
            new_end = request.data.get("new_end_time")

            if not all([new_date, new_start, new_end]):
                return Response(
                    {"detail": "Fecha y horas son obligatorias al aceptar."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conflict = Appointment.objects.filter(
                inspector=appointment.inspector,
                scheduled_date=new_date,
                status__in=[
                    AppointmentStatus.PENDING_CONFIRMATION,
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.PENDING_RESCHEDULE,
                ],
            ).exclude(pk=appointment.pk).filter(
                start_time__lt=new_end,
                end_time__gt=new_start,
            ).exists()

            if conflict:
                return Response(
                    {"detail": "El inspector ya tiene una cita en ese horario."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            appointment.scheduled_date = new_date
            appointment.start_time = new_start
            appointment.end_time = new_end
            appointment.status = AppointmentStatus.CONFIRMED
            appointment.notes = ""
            appointment.save(update_fields=["scheduled_date", "start_time", "end_time", "status", "notes"])

            msg = f"Tu solicitud de reprogramación fue aceptada. Nueva fecha: {new_date} {new_start}-{new_end}."
        else:
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancel_reason = "Reprogramación rechazada por el empleado"
            appointment.save(update_fields=["status", "cancel_reason"])

            case_file = appointment.case_file
            case_file.status = CaseFileStatus.DOCUMENTS_APPROVED
            case_file.save(update_fields=["status"])

            msg = f"Tu solicitud de reprogramación fue rechazada. La cita del trámite {appointment.case_file.tracking_code} ha sido cancelada."

        from notifications.models import Notification
        Notification.objects.create(
            citizen=appointment.case_file.citizen,
            case_file=appointment.case_file,
            title="Respuesta a reprogramación",
            message=msg,
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=False, methods=["get"], url_path="available-slots")
    def available_slots(self, request):
        inspector_id = request.query_params.get("inspector_id")
        date_str = request.query_params.get("date")

        if not inspector_id or not date_str:
            return Response(
                {"detail": "inspector_id y date son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from datetime import date as date_type
        from django.utils.dateparse import parse_date

        try:
            target_date = parse_date(date_str)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Formato de fecha inválido (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booked = Appointment.objects.filter(
            inspector_id=inspector_id,
            scheduled_date=target_date,
            status__in=[
                AppointmentStatus.PENDING_CONFIRMATION,
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.PENDING_RESCHEDULE,
            ],
        ).values_list("start_time", "end_time")

        return Response({
            "date": date_str,
            "inspector_id": inspector_id,
            "booked_slots": [
                {"start": str(s), "end": str(e)} for s, e in booked
            ],
        })

    @action(detail=False, methods=["get"], url_path="calendar")
    def calendar(self, request):
        if not _is_employee(request.user):
            return Response(
                {"detail": "No autorizado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        _cancel_past_appointments()

        from django.utils.dateparse import parse_date
        start_str = request.query_params.get("start")
        end_str = request.query_params.get("end")
        inspector_id = request.query_params.get("inspector_id")

        qs = self.get_queryset().filter(
            status__in=[
                AppointmentStatus.PENDING_CONFIRMATION,
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.PENDING_RESCHEDULE,
            ],
        )

        if start_str:
            qs = qs.filter(scheduled_date__gte=parse_date(start_str))
        if end_str:
            qs = qs.filter(scheduled_date__lte=parse_date(end_str))
        if inspector_id:
            qs = qs.filter(inspector_id=inspector_id)

        serializer = AppointmentSerializer(qs, many=True)
        return Response(serializer.data)
