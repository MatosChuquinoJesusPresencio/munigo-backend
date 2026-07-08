from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=255)
    area = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
