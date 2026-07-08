from django.db import models

from records.models import ProcedureType


class Requirement(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allowed_file_type = models.CharField(max_length=255, default="pdf,jpg,jpeg,png")
    is_mandatory = models.BooleanField(default=True)
    applies_to = models.CharField(
        max_length=50, choices=ProcedureType.choices, null=True, blank=True
    )

    def __str__(self):
        return self.name
