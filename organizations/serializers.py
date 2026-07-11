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

    def validate(self, data):
        company = data["company"]
        name = data["name"]
        instance = self.instance
        exists = Establishment.objects.filter(company=company, name__iexact=name)
        if instance:
            exists = exists.exclude(pk=instance.pk)
        if exists.exists():
            raise serializers.ValidationError(
                {"name": "Ya existe un establecimiento con este nombre en esta empresa."}
            )
        return data


class CompanySerializer(serializers.ModelSerializer):
    establishments = EstablishmentSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "business_name", "ruc", "citizens", "establishments"]
        extra_kwargs = {
            "citizens": {"read_only": True},
            "ruc": {"error_messages": {"unique": "Este RUC ya está registrado."}},
        }


class CompanyListSerializer(serializers.ModelSerializer):
    establishments_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ["id", "business_name", "ruc", "establishments_count"]

    def get_establishments_count(self, obj):
        return obj.establishments.count()


class AddCitizenSerializer(serializers.Serializer):
    citizen_id = serializers.IntegerField()

    def validate_citizen_id(self, value):
        from users.models import Citizen
        if not Citizen.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ciudadano no encontrado.")
        return value
