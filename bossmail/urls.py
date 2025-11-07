# bossmail/urls.py
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", core_views.dashboard, name="dashboard"),  # existing
    path("accounts/", include("accounts.urls")),                # new auth/admin routes
    path("mappings/", core_views.mappings, name="mappings"),
    path("mappings/create/", core_views.create_mapping, name="create_mapping"),
    path("mappings/<int:pk>/delete/", core_views.delete_mapping, name="delete_mapping"),
    path("employees/", core_views.employees, name="employees"),
    path("clients/", core_views.clients, name="clients"),
    path("messages/<int:pk>/modal/", core_views.message_modal, name="message_modal"),
    path("seed-demo/", core_views.seed_demo_view, name="seed_demo"),


    path("onboarding/", core_views.admin_dashboard, name="employee_onboarding"),
    path("code/reveal", core_views.admin_code_reveal, name="admin_code_reveal"),
    path("code/regen", core_views.admin_code_regen, name="admin_code_regen"),
    path("employees/<int:employee_id>/approve", core_views.admin_employee_approve, name="admin_employee_approve"),
    

]

    
    
    