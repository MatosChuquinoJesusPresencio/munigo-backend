from rest_framework import serializers

from procedures.models import CaseFile


class CaseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseFile
        fields = [
            "id", "tracking_code", "created_at",
            "citizen", "establishment",
            "procedure_type", "risk_level", "status",
        ]
        read_only_fields = ["tracking_code", "created_at", "risk_level", "status"]

    def validate_establishment(self, value):
        from organizations.models import Establishment
        est = Establishment.objects.select_related("company").get(id=value.id)
        if not est.company.citizens.filter(user=self.context["request"].user).exists():
            raise serializers.ValidationError(
                "No eres ciudadano de la empresa de este establecimiento."
            )
        return value

    def create(self, validated_data):
        import uuid
        establishment = validated_data["establishment"]
        validated_data["risk_level"] = establishment.get_risk_level()
        validated_data["tracking_code"] = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)
