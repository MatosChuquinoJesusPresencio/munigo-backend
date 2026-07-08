from django.db import models


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "PROGRAMADA", "Programada"
    COMPLETED = "COMPLETADA", "Completada"
    CANCELED = "CANCELADA", "Cancelada"


class Appointment(models.Model):
    record = models.ForeignKey("records.Record", on_delete=models.CASCADE)
    officer = models.ForeignKey(
        "employees.Employee", on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )

    def __str__(self):
        return f"{self.record.tracking_code} - {self.date}"
