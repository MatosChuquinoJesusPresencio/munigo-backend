from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    CITIZEN = "CIUDADANO", "Ciudadano"
    INSPECTOR = "INSPECTOR", "Inspector"
    OFFICIAL = "FUNCIONARIO", "Funcionario"
    MANAGER = "GERENTE", "Gerente"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN,
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
