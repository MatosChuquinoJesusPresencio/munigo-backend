from django.db import models


class ValidationStatus(models.TextChoices):
    PENDING = "PENDIENTE", "Pendiente"
    APPROVED = "APROBADO", "Aprobado"
    OBSERVED = "OBSERVADO", "Observado"


class Attachment(models.Model):
    record = models.ForeignKey("records.Record", on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        "requirements.Requirement", on_delete=models.SET_NULL, null=True, blank=True
    )
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )
    observations = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
