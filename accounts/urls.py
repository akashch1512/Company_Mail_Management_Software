# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Employee onboarding
    path("auth/", views.auth_portal, name="auth_portal"),
    path("auth/callback/google/", views.auth_google_callback, name="auth_google_callback"),

    # Admin access
    path("admin_login/", views.admin_login, name="admin_login"),
    path("admin/logout", views.admin_logout, name="admin_logout"),
    
    # Employee area
    path("employee/dashboard/", views.employee_dashboard, name="employee_dashboard"),
]
