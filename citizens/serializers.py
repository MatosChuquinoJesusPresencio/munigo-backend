from rest_framework import serializers
from .models import Citizen


class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = ['id', 'document_type', 'document_number', 'legal_name', 'phone', 'address']

    def validate_document_number(self, value):
        user = self.context.get('request').user if 'request' in self.context else None
        qs = Citizen.objects.filter(document_number=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El número de documento ya está registrado")
        return value
