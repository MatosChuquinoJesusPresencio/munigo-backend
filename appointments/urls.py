from django.urls import path
from . import views

urlpatterns = [
    path('availability/', views.availability, name='appointment-availability'),
    path('', views.schedule_appointment, name='schedule-appointment'),
    path('mine/', views.my_appointments, name='my-appointments'),
    path('officer/', views.officer_appointments, name='officer-appointments'),
    path('<int:pk>/', views.appointment_detail, name='appointment-detail'),
]
