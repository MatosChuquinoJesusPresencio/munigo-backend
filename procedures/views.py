from rest_framework import viewsets, permissions, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from procedures.models import (
    CaseFile, CaseFileStatus, Requirement, Appointment,
    ProcedureRequirement, AttachedDocument, ValidationStatus,
)
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
        user = self.request.user
        if hasattr(user, 'citizen') and hasattr(user.citizen, 'employee'):
            return CaseFile.objects.select_related(
                'establishment', 'establishment__company', 'citizen__user'
            ).all()
        return CaseFile.objects.select_related(
            'establishment', 'establishment__company'
        ).filter(citizen__user=user)

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
        qs = CaseFile.objects.select_related(
            "establishment", "establishment__company", "citizen__user"
        ).filter(status=CaseFileStatus.PENDING_REVIEW)
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        qs = CaseFile.objects.select_related(
            "establishment", "establishment__company", "citizen__user"
        ).exclude(status=CaseFileStatus.PENDING_REVIEW).exclude(status=CaseFileStatus.DRAFT)
        serializer = CaseFileListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="approve-documents")
    def approve_documents(self, request, pk=None):
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
            employee = user.citizen.employee
        except AttributeError:
            return Response(
                {"detail": "El usuario no es un empleado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        Appointment.objects.create(
            case_file=case_file,
            created_by=employee,
            inspector=inspector,
            scheduled_date=data["scheduled_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

        case_file.status = CaseFileStatus.PENDING_INSPECTION
        case_file.save(update_fields=["status"])

        from notifications.models import Notification
        Notification.objects.create(
            citizen=case_file.citizen,
            case_file=case_file,
            title="Inspección programada",
            message=f"Se programó una inspección para tu trámite {case_file.tracking_code}.",
        )

        return Response(CaseFileDetailSerializer(case_file).data)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
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
            case_file.save(update_fields=["status"])

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

    def get_queryset(self):
        return Appointment.objects.select_related('case_file', 'case_file__establishment', 'inspector__citizen__user').filter(case_file__citizen__user=self.request.user)
