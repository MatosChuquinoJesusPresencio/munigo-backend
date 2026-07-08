from django.db import models


class InspectionResult(models.TextChoices):
    PENDING = "PENDIENTE", "Pendiente"
    APPROVED = "APROBADO", "Aprobado"
    NOT_APPROVED = "NO_APROBADO", "No aprobado"


class Inspection(models.Model):
    record = models.ForeignKey("records.Record", on_delete=models.CASCADE)
    inspector = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE
    )
    result = models.CharField(
        max_length=20,
        choices=InspectionResult.choices,
        default=InspectionResult.PENDING,
    )
    comments = models.TextField(blank=True)
    photo_path = models.CharField(max_length=500, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    execution_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inspection {self.record.tracking_code}"
