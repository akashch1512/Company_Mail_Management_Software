# accounts/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from core.models import Org, Employee
from .decorators import admin_required, employee_required
from .forms import SpecialCodeForm, AdminLoginForm
from .services import get_org_by_code, create_or_attach_employee
from . import oauth

# ---------- Employee onboarding ----------

@require_http_methods(["GET", "POST"])
def auth_portal(request):
    """
    /auth - Employee enters special code, then continues to Google OAuth.
    Shows an 'Admin Login' link to /admin_login (top-right in template later).
    """
    if request.method == "POST":
        form = SpecialCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].strip().upper()
            org = get_org_by_code(code)
            if not org:
                messages.error(request, "Invalid company code.")
                return redirect("auth_portal")
            # Hold org info in session until OAuth finishes
            request.session["pending_org_id"] = org.id
            request.session["pending_code"] = code
            return oauth.google_start(request)  # redirects to Google
    else:
        form = SpecialCodeForm()
    return render(request, "accounts/auth_portal.html", {"form": form})

def auth_google_callback(request):
    """
    /auth/callback/google - Finish OAuth, create/attach Employee under Org, login user.
    """
    # Recover org from session
    org_id = request.session.get("pending_org_id")
    if not org_id:
        messages.error(request, "Session expired. Please enter your company code again.")
        return redirect("auth_portal")
    org = get_object_or_404(Org, id=org_id)

    email, name, tokens = oauth.google_finish(request)

    if not email:
        messages.error(request, "Google sign-in failed.")
        return redirect("auth_portal")

    emp = create_or_attach_employee(org=org, google_email=email, display_name=name)
    # Optionally persist tokens to a ProviderAuth model (add later)
    # ProviderAuth.objects.update_or_create(employee=emp, provider="gmail", defaults={...})

    # Log user in
    login(request, emp.user)
    messages.success(request, "Signed in successfully. Waiting for admin approval." if not emp.approved else "Signed in.")
    return redirect("employee_dashboard")

# ---------- Admin login & dashboard ----------

@require_http_methods(["GET", "POST"])
def admin_login(request):
    """
    /admin_login - Custom admin login page (no Django /admin exposure).
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("dashboard")

    form = AdminLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(request, username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid credentials or not an admin account.")
    return render(request, "accounts/admin_login.html", {"form": form})

def admin_logout(request):
    logout(request)
    return redirect("admin_login")

# ---------- Employee area ----------

@employee_required
def employee_dashboard(request):
    emp = request.user.employee
    # Gate if not approved (can still show status)
    return render(request, "accounts/employee_dashboard.html", {"employee": emp})
