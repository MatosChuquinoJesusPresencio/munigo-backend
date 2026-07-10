from django.contrib import admin

from organizations.models import Company, Establishment


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["business_name", "ruc"]


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "address"]
