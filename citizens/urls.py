from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.citizen_profile, name='citizen-profile'),
]
