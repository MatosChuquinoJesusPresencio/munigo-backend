from django.db import models


class BusinessCategory(models.TextChoices):
    RESTAURANT = "RESTAURANT", "Restaurante"
    COMMERCE = "COMERCIO", "Comercio"
    WAREHOUSE = "ALMACEN", "Almacén"
    SERVICES = "SERVICIOS", "Servicios"
    INDUSTRY = "INDUSTRIA", "Industria"


RISK_MATRIX = {
    "RESTAURANT": {"PEQUENO": "MEDIO", "MEDIANO": "ALTO", "GRANDE": "ALTO"},
    "COMERCIO": {"PEQUENO": "BAJO", "MEDIANO": "MEDIO", "GRANDE": "ALTO"},
    "ALMACEN": {"PEQUENO": "MEDIO", "MEDIANO": "ALTO", "GRANDE": "ALTO"},
    "SERVICIOS": {"PEQUENO": "BAJO", "MEDIANO": "BAJO", "GRANDE": "MEDIO"},
    "INDUSTRIA": {"PEQUENO": "ALTO", "MEDIANO": "ALTO", "GRANDE": "ALTO"},
}


class Company(models.Model):
    business_name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=11, unique=True)

    citizens = models.ManyToManyField(
        "users.Citizen",
        related_name="companies",
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return f"{self.business_name} - {self.ruc}"


class Establishment(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="establishments",
    )

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    business_category = models.CharField(
        max_length=20,
        choices=BusinessCategory.choices,
    )
    square_meters = models.PositiveIntegerField()

    @property
    def size(self) -> str:
        if self.square_meters <= 50:
            return "PEQUENO"
        if self.square_meters <= 200:
            return "MEDIANO"
        return "GRANDE"

    class Meta:
        verbose_name = "Establecimiento"
        verbose_name_plural = "Establecimientos"

    def __str__(self):
        return f"{self.name} - {self.address}"

    def get_risk_level(self) -> str:
        return RISK_MATRIX.get(self.business_category, {}).get(self.size, "BAJO")
