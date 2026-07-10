from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.TextChoices):
    CITIZEN = "CITIZEN", "Ciudadano"
    EMPLOYEE = "EMPLOYEE", "Empleado"


class Position(models.TextChoices):
    MANAGER = "MANAGER", "Gerente"
    INSPECTOR = "INSPECTOR", "Inspector"
    OFFICIAL = "OFFICIAL", "Funcionario"


class DocumentType(models.TextChoices):
    DNI = "DNI", "DNI"
    RUC = "RUC", "RUC"
    FOREIGN_ID_CARD = "FOREIGN_ID_CARD", "Carné de Extranjería"
    PASSPORT = "PASSPORT", "Pasaporte"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN,
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username


class Citizen(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="citizen",
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.DNI,
    )
    document_number = models.CharField(max_length=22, unique=True)

    class Meta:
        verbose_name = "Ciudadano"
        verbose_name_plural = "Ciudadanos"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.document_number}"


class Employee(models.Model):
    citizen = models.OneToOneField(
        Citizen,
        on_delete=models.CASCADE,
        related_name="employee",
    )
    position = models.CharField(max_length=20, choices=Position.choices)
    area = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def __str__(self):
        return (
            f"{self.citizen.user.get_full_name()} - {self.get_position_display()}"
        )


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token bloqueado"
        verbose_name_plural = "Tokens bloqueados"

    def __str__(self):
        return f"Blacklisted {self.token[:20]}..."
