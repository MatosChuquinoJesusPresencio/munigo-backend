from rest_framework import serializers

from inspections.models import Inspection


class InspectionSerializer(serializers.ModelSerializer):
    case_file_tracking = serializers.CharField(source='appointment.case_file.tracking_code', read_only=True)
    case_file_procedure_type = serializers.SerializerMethodField()
    establishment_name = serializers.CharField(source='appointment.case_file.establishment.name', read_only=True)
    establishment_address = serializers.CharField(source='appointment.case_file.establishment.address', read_only=True)
    scheduled_date = serializers.DateField(source='appointment.scheduled_date', read_only=True)
    start_time = serializers.TimeField(source='appointment.start_time', read_only=True)
    end_time = serializers.TimeField(source='appointment.end_time', read_only=True)
    risk_level = serializers.CharField(source='appointment.case_file.risk_level', read_only=True)

    class Meta:
        model = Inspection
        fields = [
            "id", "appointment", "result", "comments", "photo_urls", "executed_at",
            "case_file_tracking", "case_file_procedure_type",
            "establishment_name", "establishment_address",
            "scheduled_date", "start_time", "end_time", "risk_level",
        ]
        read_only_fields = ["executed_at"]

    def get_case_file_procedure_type(self, obj):
        return obj.appointment.case_file.get_procedure_type_display()

    def validate_appointment(self, value):
        if hasattr(value, "inspection"):
            raise serializers.ValidationError("Esta cita ya tiene una inspección registrada.")
        return value
