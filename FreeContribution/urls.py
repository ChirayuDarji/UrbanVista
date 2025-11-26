from django.urls import path
from . import views

app_name = "FreeContribution"

urlpatterns = [
    # Home page: list of travel experiences
    path("", views.experience_home, name="experience_home"),

    # List by type (place, activity, story, tip)
    path("type/<str:experience_type>/", views.experience_list_by_type, name="experience_list_by_type"),

    # Create a new experience (optionally by type)
    path("create/", views.experience_create, name="experience_create"),
    path("create/<str:experience_type>/", views.experience_create, name="experience_create_type"),

    # Detail page for a travel experience
    path("experience/<slug:slug>/", views.experience_detail, name="experience_detail"),

    # Upvote toggle (AJAX/API)
    path("api/<uuid:pk>/upvote/", views.toggle_experience_upvote, name="toggle_experience_upvote"),

    # Bookmark toggle (AJAX/API)
    path("api/<uuid:pk>/bookmark/", views.toggle_experience_bookmark, name="toggle_experience_bookmark"),

    # Map data API (for showing experiences on a map)
    path("api/map/", views.experience_map_data, name="experience_map_data"),
]