from django.urls import path, include
from rest_framework.routers import DefaultRouter

from procedures.views import (
    CaseFileViewSet,
    RequirementViewSet,
    AppointmentViewSet,
    ProcedureRequirementViewSet,
    AttachedDocumentViewSet,
)

router = DefaultRouter()
router.register(r"case-files", CaseFileViewSet, basename="case-file")
router.register(r"requirements", RequirementViewSet, basename="requirement")
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"procedure-requirements", ProcedureRequirementViewSet, basename="procedure-requirement")
router.register(r"attached-documents", AttachedDocumentViewSet, basename="attached-document")

urlpatterns = [
    path("", include(router.urls)),
]
