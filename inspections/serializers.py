from rest_framework import serializers
from .models import Inspection


class AssignInspectionSerializer(serializers.Serializer):
    record_id = serializers.IntegerField()
    inspector_id = serializers.IntegerField()
    scheduled_date = serializers.DateTimeField(required=False, allow_null=True)


class InspectionResultSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=['APROBADO', 'NO_APROBADO'])
    comments = serializers.CharField(required=False, allow_blank=True)


class InspectionSerializer(serializers.ModelSerializer):
    record_tracking = serializers.CharField(source='record.tracking_code', read_only=True)
    record_address = serializers.CharField(source='record.premises_address', read_only=True)
    record_zone = serializers.CharField(source='record.zone', read_only=True)
    inspector_name = serializers.SerializerMethodField()
    business_type = serializers.CharField(source='record.business_type', read_only=True)

    class Meta:
        model = Inspection
        fields = [
            'id', 'record', 'record_tracking', 'inspector', 'inspector_name',
            'result', 'comments', 'photo_path',
            'scheduled_date', 'execution_date', 'created_at',
            'record_address', 'record_zone', 'business_type',
        ]

    def get_inspector_name(self, obj):
        return f"{obj.inspector.first_name} {obj.inspector.last_name}"


class RouteSheetItemSerializer(serializers.Serializer):
    inspection_id = serializers.IntegerField()
    record_id = serializers.IntegerField()
    tracking_code = serializers.CharField()
    address = serializers.CharField()
    zone = serializers.CharField()
    business_type = serializers.CharField()
    scheduled_date = serializers.DateTimeField()


class RouteSheetSerializer(serializers.Serializer):
    inspector_id = serializers.IntegerField()
    inspector_name = serializers.CharField()
    date = serializers.DateField()
    inspections = RouteSheetItemSerializer(many=True)
