from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Citizen, Employee, BlacklistedToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_staff"]
    list_filter = ["role", "is_staff", "is_active"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )


@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ["user", "document_type", "document_number"]
    search_fields = ["document_number", "user__username"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["citizen", "position", "area"]
    list_filter = ["position", "area"]


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ["token", "blacklisted_at"]
    readonly_fields = ["token", "blacklisted_at"]
