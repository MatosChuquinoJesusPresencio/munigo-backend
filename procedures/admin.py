from django.contrib import admin

from procedures.models import CaseFile, Requirement, AttachedDocument, ProcedureRequirement


@admin.register(CaseFile)
class CaseFileAdmin(admin.ModelAdmin):
    list_display = ["tracking_code", "citizen", "procedure_type", "status", "created_at"]
    list_filter = ["procedure_type", "status", "risk_level"]
    search_fields = ["tracking_code", "citizen__user__username"]


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ["name", "procedure_type", "is_required", "allowed_formats"]
    list_filter = ["procedure_type", "is_required"]


@admin.register(ProcedureRequirement)
class ProcedureRequirementAdmin(admin.ModelAdmin):
    list_display = ["case_file", "requirement", "fulfilled"]
    list_filter = ["fulfilled"]


@admin.register(AttachedDocument)
class AttachedDocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "procedure_requirement", "validation_status", "uploaded_at"]
    list_filter = ["validation_status"]
