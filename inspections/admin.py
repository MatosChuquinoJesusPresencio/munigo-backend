from django.contrib import admin

from inspections.models import Inspection


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ["appointment", "result", "executed_at"]
    list_filter = ["result"]
