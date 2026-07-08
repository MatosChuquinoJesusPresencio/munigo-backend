from django.db import models


class Notification(models.Model):
    citizen = models.ForeignKey("citizens.Citizen", on_delete=models.CASCADE)
    record = models.ForeignKey(
        "records.Record", on_delete=models.CASCADE, null=True, blank=True
    )
    type = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.citizen.legal_name}"
