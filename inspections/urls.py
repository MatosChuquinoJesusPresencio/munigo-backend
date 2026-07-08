from django.urls import path

from . import views

urlpatterns = [
    path("assign/", views.assign_inspection, name="assign-inspection"),
    path("route-sheet/", views.route_sheet, name="route-sheet"),
    path("mine/", views.my_inspections, name="my-inspections"),
    path("<int:pk>/", views.inspection_detail, name="inspection-detail"),
    path("<int:pk>/result/", views.register_result, name="register-result"),
    path("by-record/<int:record_id>/", views.inspections_by_record, name="inspections-by-record"),
]
