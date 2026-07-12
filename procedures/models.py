from django.db import models


class ProcedureType(models.TextChoices):
    OPERATING_LICENSE = "LICENCIA_DE_FUNCIONAMIENTO", "Licencia de Funcionamiento"
    ITSE = "ITSE", "ITSE"


class AllowedFormat(models.TextChoices):
    PDF = "PDF", "PDF"
    PNG = "PNG", "PNG"
    JPG = "JPG", "JPG"
    JPEG = "JPEG", "JPEG"


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


class ValidationStatus(models.TextChoices):
    PENDING = "PENDIENTE", "Pendiente"
    APPROVED = "APROBADO", "Aprobado"
    OBSERVED = "OBSERVADO", "Observado"


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "PROGRAMADA", "Programada"
    COMPLETED = "COMPLETADA", "Completada"
    CANCELLED = "CANCELADA", "Cancelada"


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
        db_index=True,
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
    )

    status = models.CharField(
        max_length=50,
        choices=CaseFileStatus.choices,
        default=CaseFileStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"

    def __str__(self):
        return f"{self.tracking_code} - {self.get_procedure_type_display()}"


class Requirement(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allowed_formats = models.JSONField(default=list)
    is_required = models.BooleanField(default=True)
    procedure_type = models.CharField(
        max_length=50,
        choices=ProcedureType.choices,
        db_index=True,
    )

    class Meta:
        verbose_name = "Requisito"
        verbose_name_plural = "Requisitos"

    def __str__(self):
        return self.name


class ProcedureRequirement(models.Model):
    case_file = models.ForeignKey(
        CaseFile,
        on_delete=models.CASCADE,
        related_name="procedure_requirements",
    )
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
    )
    fulfilled = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Requisito del expediente"
        verbose_name_plural = "Requisitos del expediente"
        constraints = [
            models.UniqueConstraint(
                fields=["case_file", "requirement"],
                name="unique_case_file_requirement",
            )
        ]

    def __str__(self):
        return f"{self.case_file.tracking_code} - {self.requirement.name}"


class AttachedDocument(models.Model):
    procedure_requirement = models.ForeignKey(
        ProcedureRequirement,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=500)
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )
    observations = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento adjunto"
        verbose_name_plural = "Documentos adjuntos"

    def __str__(self):
        return self.name


class Appointment(models.Model):
    case_file = models.ForeignKey(
        CaseFile,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    created_by = models.ForeignKey(
        "users.Employee",
        on_delete=models.CASCADE,
        related_name="created_appointments",
    )
    inspector = models.ForeignKey(
        "users.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
        db_index=True,
    )

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.case_file.tracking_code} - {self.scheduled_date}"