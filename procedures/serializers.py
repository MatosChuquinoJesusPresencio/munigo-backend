from rest_framework import serializers

from procedures.models import CaseFile, Requirement, AllowedFormat, Appointment


class RequirementSerializer(serializers.ModelSerializer):
    allowed_formats = serializers.ListField(
        child=serializers.ChoiceField(choices=AllowedFormat.choices),
    )

    class Meta:
        model = Requirement
        fields = "__all__"


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

    class Meta:
        model = CaseFile
        fields = [
            "id", "tracking_code", "created_at",
            "citizen", "establishment", "establishment_name", "company_name",
            "procedure_type", "risk_level", "status",
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
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=None)

    class Meta:
        model = Appointment
        fields = [
            "id", "case_file", "created_by", "inspector",
            "scheduled_date", "start_time", "end_time", "status",
        ]
        read_only_fields = ["status"]

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
