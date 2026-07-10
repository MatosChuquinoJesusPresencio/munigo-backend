from django.contrib import admin

from procedures.models import CaseFile


@admin.register(CaseFile)
class CaseFileAdmin(admin.ModelAdmin):
    list_display = ["tracking_code", "citizen", "procedure_type", "status", "created_at"]
    list_filter = ["procedure_type", "status", "risk_level"]
    search_fields = ["tracking_code", "citizen__user__username"]
