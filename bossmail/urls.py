from django.contrib import admin
from django.urls import path
from core import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("messages/<int:pk>/modal/", views.message_modal, name="message_modal"),
    path("mappings/", views.mappings, name="mappings"),
    path("mappings/create/", views.create_mapping, name="create_mapping"),
    path("mappings/<int:pk>/delete/", views.delete_mapping, name="delete_mapping"),
    path("employees/", views.employees, name="employees"),
    path("clients/", views.clients, name="clients"),
    path("seed-demo/", views.seed_demo_view, name="seed_demo"), # dev-only
]