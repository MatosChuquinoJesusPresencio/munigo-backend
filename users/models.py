from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    CIUDADANO = "CIUDADANO", "Ciudadano"
    INSPECTOR = "INSPECTOR", "Inspector"
    FUNCIONARIO = "FUNCIONARIO", "Funcionario"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CIUDADANO,
    )
