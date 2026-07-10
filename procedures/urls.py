from django.urls import path, include
from rest_framework.routers import DefaultRouter

from procedures.views import CaseFileViewSet

router = DefaultRouter()
router.register(r"case-files", CaseFileViewSet, basename="case-file")

urlpatterns = [
    path("", include(router.urls)),
]
