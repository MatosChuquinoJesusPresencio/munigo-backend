from django.db import models    


class Company(models.Model):
    business_name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=11, unique=True)

    citizens = models.ManyToManyField(
        "users.Citizen",
        related_name="companies"
    )


class Establishment(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="establishments"
    )

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)