from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField()
    approval_rate = serializers.FloatField()
    new_this_month = serializers.IntegerField()
    total_citizens = serializers.IntegerField()
    total_inspectors = serializers.IntegerField()
    total_officials = serializers.IntegerField()


class AvgTimeItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    avg_days = serializers.FloatField()


class AvgTimeSerializer(serializers.Serializer):
    overall_avg_days = serializers.FloatField()
    by_procedure_type = AvgTimeItemSerializer(many=True)
    by_risk_level = AvgTimeItemSerializer(many=True)


class RiskItemSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class RiskDistributionSerializer(serializers.Serializer):
    low = RiskItemSerializer()
    medium = RiskItemSerializer()
    high = RiskItemSerializer()
    total = serializers.IntegerField()


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    position = serializers.CharField()
    area = serializers.CharField()
    inspections_assigned = serializers.IntegerField()
    inspections_completed = serializers.IntegerField()
    approval_rate = serializers.FloatField()


class SlowRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tracking_code = serializers.CharField()
    citizen = serializers.CharField()
    status = serializers.CharField()
    risk_level = serializers.CharField()
    procedure_type = serializers.CharField()
    days_in_state = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class ExpiryItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tracking_code = serializers.CharField()
    citizen = serializers.CharField()
    status = serializers.CharField()
    days_passed = serializers.IntegerField()


class ExpiryAlertsSerializer(serializers.Serializer):
    expired = ExpiryItemSerializer(many=True)
    expiring_soon = ExpiryItemSerializer(many=True)
    total_expired = serializers.IntegerField()
    total_expiring_soon = serializers.IntegerField()


class SummarySerializer(serializers.Serializer):
    pending_review = serializers.IntegerField()
    pending_inspection = serializers.IntegerField()
    observed = serializers.IntegerField()
    approved_this_month = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    pending_inspections_today = serializers.IntegerField()
