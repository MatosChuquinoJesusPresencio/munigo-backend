from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.urls import path, include


def health_check(request):
    return JsonResponse({"status": "ok"})


def favicon(request):
    return HttpResponse(status=204)


urlpatterns = [
    path('', health_check, name='health_check'),
    path('favicon.ico', favicon, name='favicon'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/organizations/', include('organizations.urls')),
    path('api/procedures/', include('procedures.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/inspections/', include('inspections.urls')),
]
