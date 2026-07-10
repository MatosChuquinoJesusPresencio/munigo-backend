from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "case_file", "is_read", "sent_at"]
        read_only_fields = ["title", "message", "case_file", "sent_at"]
