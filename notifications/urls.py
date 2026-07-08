from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_notifications, name='notifications-list'),
    path('unread/', views.list_unread, name='notifications-unread'),
    path('<int:pk>/read/', views.mark_as_read, name='notification-mark-read'),
    path('mark-all-read/', views.mark_all_read, name='notifications-mark-all-read'),
]
