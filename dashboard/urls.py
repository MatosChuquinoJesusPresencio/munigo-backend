from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.general_stats, name='dashboard-stats'),
    path('avg-time/', views.avg_time, name='dashboard-avg-time'),
    path('risk-distribution/', views.risk_distribution, name='dashboard-risk-distribution'),
    path('officer-performance/', views.officer_performance, name='dashboard-officer-performance'),
    path('slow-records/', views.slow_records, name='dashboard-slow-records'),
    path('expiry-alerts/', views.expiry_alerts, name='dashboard-expiry-alerts'),
    path('summary/', views.summary, name='dashboard-summary'),
]
