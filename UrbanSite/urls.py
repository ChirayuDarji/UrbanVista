# UrbanSite/urls.py
from django.urls import path
from . import views

app_name = 'urbansite'

urlpatterns = [
    path('report/', views.report_issue, name='report_issue'),
    path('success/<int:report_id>/', views.success, name='success'),
    path('not-allowed/', views.not_allowed, name='not_allowed'),
]

