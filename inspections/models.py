from django.db import models


class InspectionResult(models.TextChoices):
    APPROVED = "APROBADO", "Aprobado"
    REJECTED = "NO_APROBADO", "No aprobado"


class Inspection(models.Model):
    appointment = models.OneToOneField(
        "procedures.Appointment",
        on_delete=models.CASCADE,
        related_name="inspection",
    )
    result = models.CharField(
        max_length=20,
        choices=InspectionResult.choices,
    )
    comments = models.TextField(blank=True)
    photo_urls = models.JSONField(default=list, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inspección"
        verbose_name_plural = "Inspecciones"

    def __str__(self):
        return f"Inspección - {self.appointment.case_file.tracking_code}"
