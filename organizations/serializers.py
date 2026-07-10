from rest_framework import serializers
from organizations.models import Company, Establishment


class EstablishmentSerializer(serializers.ModelSerializer):
    size = serializers.CharField(read_only=True)

    class Meta:
        model = Establishment
        fields = [
            "id", "company", "name", "address",
            "business_category", "square_meters", "size",
        ]


class CompanySerializer(serializers.ModelSerializer):
    establishments = EstablishmentSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "business_name", "ruc", "citizens", "establishments"]
        extra_kwargs = {"citizens": {"read_only": True}}


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "business_name", "ruc"]


class AddCitizenSerializer(serializers.Serializer):
    citizen_id = serializers.IntegerField()

    def validate_citizen_id(self, value):
        from users.models import Citizen
        if not Citizen.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ciudadano no encontrado.")
        return value
