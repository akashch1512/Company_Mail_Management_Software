# accounts/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view):
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated:
            return redirect("admin_login")
        if not (u.is_staff or u.is_superuser):
            messages.error(request, "Admin access required.")
            return redirect("admin_login")
        return view(request, *args, **kwargs)
    return _wrapped

def employee_required(view):
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated or not hasattr(u, "employee"):
            return redirect("auth_portal")
        return view(request, *args, **kwargs)
    return _wrapped
