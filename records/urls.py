from django.urls import path
from . import views
from attachments.views import record_documents

urlpatterns = [
    path('', views.create_record, name='create-record'),
    path('mine/', views.list_my_records, name='my-records'),
    path('classify-risk/', views.classify_risk, name='classify-risk'),
    path('pending-review/', views.list_pending_review, name='pending-review'),
    path('<int:pk>/', views.record_detail_update, name='record-detail'),
    path('<int:pk>/submit/', views.submit_record, name='submit-record'),
    path('<int:pk>/resubmit/', views.resubmit_record, name='resubmit-record'),
    path('<int:pk>/documents/', record_documents, name='record-documents'),
]

evaluation_urlpatterns = [
    path('pending/', views.list_pending_review, name='eval-pending'),
    path('records/<int:pk>/', views.review_record_detail, name='eval-record-detail'),
    path('records/<int:pk>/documents/', views.review_record_documents, name='eval-record-documents'),
    path('documents/validate/', views.validate_document, name='eval-validate-document'),
    path('records/<int:pk>/finalize/', views.finalize_review, name='eval-finalize'),
    path('records/<int:pk>/risk/', views.reclassify_risk, name='eval-reclassify-risk'),
]
