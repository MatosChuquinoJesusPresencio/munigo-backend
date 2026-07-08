from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    record_tracking = serializers.CharField(source='record.tracking_code', read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'citizen', 'record', 'record_tracking',
            'type', 'message', 'is_read', 'sent_at',
        ]


class NotificationListSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    notifications = NotificationSerializer(many=True)
