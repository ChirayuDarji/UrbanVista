# reports/urls.py

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('create/', views.report_create, name='report_create'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/edit/', views.report_edit, name='report_edit'),  # optional
    path('<int:pk>/delete/', views.report_delete, name='report_delete'),  # optional
    
    # New features - no DB changes
    path('statistics/', views.statistics_dashboard, name='statistics'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),
]