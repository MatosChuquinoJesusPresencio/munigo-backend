from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "citizen", "is_read", "sent_at"]
    list_filter = ["is_read"]
    search_fields = ["citizen__user__username", "title"]
