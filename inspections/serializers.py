from rest_framework import serializers

from inspections.models import Inspection


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = ["id", "appointment", "result", "comments", "photo_urls", "executed_at"]
        read_only_fields = ["executed_at"]

    def validate_appointment(self, value):
        if hasattr(value, "inspection"):
            raise serializers.ValidationError("Esta cita ya tiene una inspección registrada.")
        return value
