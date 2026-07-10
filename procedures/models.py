from django.db import models


class ProcedureType(models.TextChoices):
    OPERATING_LICENSE = "LICENCIA_DE_FUNCIONAMIENTO", "Licencia de Funcionamiento"
    ITSE = "ITSE", "ITSE"


class RiskLevel(models.TextChoices):
    LOW = "BAJO", "Bajo"
    MEDIUM = "MEDIO", "Medio"
    HIGH = "ALTO", "Alto"


class CaseFileStatus(models.TextChoices):
    DRAFT = "BORRADOR", "Borrador"
    PENDING_REVIEW = "PENDIENTE_DE_REVISION", "Pendiente de revisión"
    DOCUMENTS_APPROVED = "DOCUMENTOS_APROBADOS", "Documentos aprobados"
    PENDING_INSPECTION = "PENDIENTE_DE_INSPECCION", "Pendiente de inspección"
    APPROVED = "APROBADO", "Aprobado"
    OBSERVED = "OBSERVADO", "Observado"
    REJECTED = "RECHAZADO", "Rechazado"


class CaseFile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    tracking_code = models.CharField(max_length=20, unique=True)

    citizen = models.ForeignKey(
        "users.Citizen",
        on_delete=models.CASCADE,
        related_name="case_files",
    )
    establishment = models.ForeignKey(
        "organizations.Establishment",
        on_delete=models.CASCADE,
        related_name="case_files",
    )

    procedure_type = models.CharField(
        max_length=50,
        choices=ProcedureType.choices,
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
    )

    status = models.CharField(
        max_length=50,
        choices=CaseFileStatus.choices,
        default=CaseFileStatus.DRAFT,
    )

    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"

    def __str__(self):
        return f"{self.tracking_code} - {self.get_procedure_type_display()}"
