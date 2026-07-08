from rest_framework import serializers
from .models import Appointment


class AppointmentCreateSerializer(serializers.Serializer):
    record_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    officer_id = serializers.IntegerField(required=False, allow_null=True)


class AppointmentSerializer(serializers.ModelSerializer):
    record_tracking = serializers.CharField(source='record.tracking_code', read_only=True)
    officer_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'record', 'record_tracking', 'officer', 'officer_name',
            'date', 'start_time', 'end_time', 'status',
        ]

    def get_officer_name(self, obj):
        if obj.officer:
            return f"{obj.officer.first_name} {obj.officer.last_name}"
        return None


class AvailabilityRequestSerializer(serializers.Serializer):
    date = serializers.DateField()


class AvailabilitySlotSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
