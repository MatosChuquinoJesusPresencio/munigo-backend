from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/documents/', views.record_documents, name='record-documents'),
]
