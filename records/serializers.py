from rest_framework import serializers
from .models import Record, ProcedureType
from citizens.serializers import CitizenSerializer


class RecordCreateSerializer(serializers.Serializer):
    procedure_type = serializers.ChoiceField(choices=ProcedureType.choices)
    business_type = serializers.CharField(max_length=255)
    premises_size = serializers.IntegerField()
    premises_address = serializers.CharField(required=False, allow_blank=True)
    zone = serializers.CharField(required=False, allow_blank=True)


class RecordUpdateSerializer(serializers.Serializer):
    procedure_type = serializers.ChoiceField(choices=ProcedureType.choices, required=False)
    business_type = serializers.CharField(max_length=255, required=False)
    premises_size = serializers.IntegerField(required=False)
    premises_address = serializers.CharField(required=False, allow_blank=True)
    zone = serializers.CharField(required=False, allow_blank=True)


class RecordSerializer(serializers.ModelSerializer):
    citizen = CitizenSerializer(read_only=True)

    class Meta:
        model = Record
        fields = [
            'id', 'citizen', 'procedure_type', 'risk_level', 'tracking_code',
            'business_type', 'premises_size', 'premises_address', 'zone',
            'status', 'created_at',
        ]


class RecordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = [
            'id', 'tracking_code', 'procedure_type', 'risk_level',
            'business_type', 'status', 'created_at',
        ]


class RiskClassificationSerializer(serializers.Serializer):
    business_type = serializers.CharField(max_length=255)
    premises_size = serializers.IntegerField()


class RiskClassificationResultSerializer(serializers.Serializer):
    risk_level = serializers.CharField()
    requires_inspection = serializers.BooleanField()
    motive = serializers.CharField()


class DocumentValidationSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    validation_status = serializers.ChoiceField(choices=['APROBADO', 'OBSERVADO'])
    observations = serializers.CharField(required=False, allow_blank=True)


class RiskReclassificationSerializer(serializers.Serializer):
    risk_level = serializers.ChoiceField(choices=['BAJO', 'MEDIO', 'ALTO'])


class RecordEvaluationSerializer(serializers.ModelSerializer):
    citizen_name = serializers.CharField(source='citizen.legal_name', read_only=True)
    document_count = serializers.SerializerMethodField()
    approved_count = serializers.SerializerMethodField()
    observed_count = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = [
            'id', 'tracking_code', 'procedure_type', 'risk_level',
            'business_type', 'premises_size', 'premises_address', 'zone',
            'status', 'created_at', 'citizen_name',
            'document_count', 'approved_count', 'observed_count',
        ]

    def get_document_count(self, obj):
        return obj.attachment_set.count()

    def get_approved_count(self, obj):
        return obj.attachment_set.filter(validation_status='APROBADO').count()

    def get_observed_count(self, obj):
        return obj.attachment_set.filter(validation_status='OBSERVADO').count()
