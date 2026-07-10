from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organizations.views import CompanyViewSet, EstablishmentViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"establishments", EstablishmentViewSet, basename="establishment")

urlpatterns = [
    path("", include(router.urls)),
]
