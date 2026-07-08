from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from records.urls import evaluation_urlpatterns
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/citizens/', include('citizens.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/records/', include('records.urls')),
    path('api/evaluation/', include(evaluation_urlpatterns)),
    path('api/appointments/', include('appointments.urls')),
    path('api/inspections/', include('inspections.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
