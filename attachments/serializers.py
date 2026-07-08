from rest_framework import serializers
from .models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'record', 'requirement', 'filename', 'file_path',
                  'validation_status', 'observations', 'uploaded_at']
        read_only_fields = ['validation_status', 'observations', 'uploaded_at', 'file_path']


class AttachmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'filename', 'file_path', 'validation_status',
                  'observations', 'uploaded_at', 'requirement']
