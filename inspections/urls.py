from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inspections.views import InspectionViewSet

router = DefaultRouter()
router.register(r"inspections", InspectionViewSet, basename="inspection")

urlpatterns = [
    path("", include(router.urls)),
]
