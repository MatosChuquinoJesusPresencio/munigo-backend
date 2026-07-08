from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.employee_profile, name='employee-profile'),
    path('inspectors/', views.inspector_list, name='inspector-list'),
]
