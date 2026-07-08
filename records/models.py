from django.db import models


class RiskLevel(models.TextChoices):
    LOW = "BAJO", "Bajo"
    MEDIUM = "MEDIO", "Medio"
    HIGH = "ALTO", "Alto"


class RecordStatus(models.TextChoices):
    DRAFT = "BORRADOR", "Borrador"
    PENDING_REVIEW = "PENDIENTE_REVISION", "Pendiente de revisión"
    DOCUMENTS_APPROVED = "DOCUMENTOS_APROBADOS", "Documentos aprobados"
    PENDING_INSPECTION = "PENDIENTE_INSPECCION", "Pendiente de inspección"
    APPROVED = "APROBADO", "Aprobado"
    OBSERVED = "OBSERVADO", "Observado"
    REJECTED = "RECHAZADO", "Rechazado"


class ProcedureType(models.TextChoices):
    OPERATING_LICENSE = "LICENCIA_FUNCIONAMIENTO", "Licencia de funcionamiento"
    ITSE = "ITSE", "ITSE"


class Record(models.Model):
    citizen = models.ForeignKey("citizens.Citizen", on_delete=models.CASCADE)
    procedure_type = models.CharField(max_length=50, choices=ProcedureType.choices)
    risk_level = models.CharField(
        max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW
    )
    tracking_code = models.CharField(max_length=50, unique=True)
    business_type = models.CharField(max_length=255)
    premises_size = models.IntegerField()
    premises_address = models.TextField(blank=True)
    zone = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=30, choices=RecordStatus.choices, default=RecordStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tracking_code}"


class RecordRequirement(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        "requirements.Requirement", on_delete=models.CASCADE
    )
    attachment = models.ForeignKey(
        "attachments.Attachment", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("record", "requirement")

    def __str__(self):
        return f"{self.record.tracking_code} - {self.requirement.name}"
