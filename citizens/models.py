from django.db import models
from django.conf import settings


class DocumentType(models.TextChoices):
    DNI = "DNI", "DNI"
    RUC = "RUC", "RUC"
    FOREIGNER_ID = "CARNET_EXTRANJERIA", "Carné de extranjería"
    PASSPORT = "PASAPORTE", "Pasaporte"


class Citizen(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, default=DocumentType.DNI
    )
    document_number = models.CharField(max_length=20, unique=True)
    legal_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.legal_name} ({self.document_number})"
