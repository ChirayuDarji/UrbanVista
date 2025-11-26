# projects/urls.py

from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # List & Detail
    path('', views.project_list, name='list'),
    path('<slug:slug>/', views.project_detail, name='detail'),
    
    # Create
    path('create/', views.project_create, name='create'),
    path('<slug:slug>/update/add/', views.project_update_add, name='update_add'),
    path('<slug:slug>/document/add/', views.project_document_add, name='document_add'),
    
    # Update
    path('<slug:slug>/edit/', views.project_edit, name='edit'),
    
    # Delete
    path('<slug:slug>/delete/', views.project_delete, name='delete'),
    path('update/<int:pk>/delete/', views.project_update_delete, name='update_delete'),
    path('document/<int:pk>/delete/', views.project_document_delete, name='document_delete'),
    
    # Category Management
    path('category/create/', views.category_create, name='category_create'),
]

