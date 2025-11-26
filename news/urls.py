from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='list'),
    path('category/<slug:slug>/', views.news_by_category, name='by_category'),
    path('<slug:slug>/', views.news_detail, name='detail'),
    # Staff manage
    path('admin/manage/', views.manage_list, name='manage'),
    path('admin/create/', views.create, name='create'),
    path('admin/<slug:slug>/edit/', views.edit, name='edit'),
    path('admin/<slug:slug>/delete/', views.delete, name='delete'),
]