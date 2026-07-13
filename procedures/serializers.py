from rest_framework import serializers

from procedures.models import (
    CaseFile, CaseFileStatus, Requirement, AllowedFormat, ValidationStatus,
    Appointment, ProcedureRequirement, AttachedDocument,
)


class RequirementSerializer(serializers.ModelSerializer):
    allowed_formats = serializers.ListField(
        child=serializers.ChoiceField(choices=AllowedFormat.choices),
    )

    class Meta:
        model = Requirement
        fields = "__all__"


class AttachedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachedDocument
        fields = ["id", "procedure_requirement", "name", "file", "validation_status", "observations", "uploaded_at"]
        read_only_fields = ["validation_status", "observations", "uploaded_at"]

    def validate_file(self, value):
        if not value.startswith('http'):
            raise serializers.ValidationError("La URL del archivo debe ser válida.")
        return value

    def validate_procedure_requirement(self, value):
        if self.instance is None:
            if AttachedDocument.objects.filter(procedure_requirement=value).exists():
                raise serializers.ValidationError("Ya existe un documento para este requisito.")
        return value


class ProcedureRequirementSerializer(serializers.ModelSerializer):
    requirement = RequirementSerializer(read_only=True)
    documents = AttachedDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = ProcedureRequirement
        fields = ["id", "requirement", "fulfilled", "documents"]


class CaseFileListSerializer(serializers.ModelSerializer):
    establishment_name = serializers.CharField(source='establishment.name', read_only=True)
    company_name = serializers.CharField(source='establishment.company.business_name', read_only=True)

    class Meta:
        model = CaseFile
        fields = [
            "id", "tracking_code", "created_at",
            "citizen", "establishment", "establishment_name", "company_name",
            "procedure_type", "risk_level", "status",
        ]


class CaseFileDetailSerializer(serializers.ModelSerializer):
    establishment_name = serializers.CharField(source='establishment.name', read_only=True)
    company_name = serializers.CharField(source='establishment.company.business_name', read_only=True)
    procedure_requirements = ProcedureRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = CaseFile
        fields = [
            "id", "tracking_code", "created_at",
            "citizen", "establishment", "establishment_name", "company_name",
            "procedure_type", "risk_level", "status", "procedure_requirements",
        ]
        read_only_fields = ["tracking_code", "created_at", "risk_level", "status", "citizen"]

    def validate_establishment(self, value):
        from organizations.models import Establishment
        est = Establishment.objects.select_related("company").get(id=value.id)
        if not est.company.citizens.filter(user=self.context["request"].user).exists():
            raise serializers.ValidationError(
                "No eres ciudadano de la empresa de este establecimiento."
            )
        return value

    def create(self, validated_data):
        import uuid
        establishment = validated_data["establishment"]
        validated_data["risk_level"] = establishment.get_risk_level()
        validated_data["tracking_code"] = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        case_file = super().create(validated_data)

        requirements = Requirement.objects.filter(procedure_type=case_file.procedure_type)
        ProcedureRequirement.objects.bulk_create([
            ProcedureRequirement(case_file=case_file, requirement=req)
            for req in requirements
        ])

        return case_file


class AppointmentSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=None)
    case_file_tracking = serializers.CharField(source='case_file.tracking_code', read_only=True)
    case_file_procedure_type = serializers.SerializerMethodField()
    establishment_name = serializers.SerializerMethodField()
    inspector_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "case_file", "case_file_tracking", "case_file_procedure_type",
            "establishment_name", "created_by", "inspector", "inspector_name",
            "scheduled_date", "start_time", "end_time", "status",
        ]
        read_only_fields = ["status"]

    def get_case_file_procedure_type(self, obj):
        return obj.case_file.get_procedure_type_display()

    def get_establishment_name(self, obj):
        return obj.case_file.establishment.name if obj.case_file.establishment else None

    def get_inspector_name(self, obj):
        if obj.inspector and hasattr(obj.inspector, 'citizen'):
            user = obj.inspector.citizen.user
            return f"{user.first_name} {user.last_name}".strip()
        return None

    def validate_created_by(self, value):
        user = self.context["request"].user
        try:
            employee = user.citizen.employee
        except AttributeError:
            raise serializers.ValidationError("El usuario no es un empleado.")

        if employee.position not in ("OFFICIAL", "MANAGER"):
            raise serializers.ValidationError(
                "Solo un funcionario o gerente puede crear citas."
            )
        return employee

    def validate_inspector(self, value):
        if value is not None and value.position != "INSPECTOR":
            raise serializers.ValidationError(
                "El inspector debe tener el cargo de Inspector."
            )
        return value

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "La hora de inicio debe ser anterior a la hora de fin."
            )
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.validate_created_by(None)
        return super().create(validated_data)


class AttachedDocumentValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachedDocument
        fields = ["validation_status", "observations"]

    def validate_validation_status(self, value):
        if value not in (ValidationStatus.APPROVED, ValidationStatus.OBSERVED):
            raise serializers.ValidationError(
                "El estado debe ser APROBADO u OBSERVADO."
            )
        return value


class AssignInspectorSerializer(serializers.Serializer):
    inspector_id = serializers.IntegerField()
    scheduled_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate_inspector_id(self, value):
        from users.models import Employee
        try:
            employee = Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("El empleado no existe.")
        if employee.position != "INSPECTOR":
            raise serializers.ValidationError("El empleado debe tener cargo de Inspector.")
        return value

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "La hora de inicio debe ser anterior a la hora de fin."
            )
        return data


class CaseFileSetStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            (CaseFileStatus.APPROVED, "Aprobado"),
            (CaseFileStatus.OBSERVED, "Observado"),
            (CaseFileStatus.REJECTED, "Rechazado"),
        ]
    )
