from django.db import models


class Notification(models.Model):
    citizen = models.ForeignKey(
        "users.Citizen",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    case_file = models.ForeignKey(
        "procedures.CaseFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-sent_at"]

    def __str__(self):
        return self.title
