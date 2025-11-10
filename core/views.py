from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from accounts.decorators import admin_required, employee_required

from .models import Org, Employee
from django.contrib import messages

from .models import Message, SenderMapping, Employee, Client
from .rules import detect_assignment

@login_required
def dashboard(request):
    # Filters
    hours = int(request.GET.get("hours", 168))  # default 7d
    assignment_only = request.GET.get("assignment", "0") == "1"
    employee_id = request.GET.get("employee")
    client_id = request.GET.get("client")

    qs = Message.objects.select_related("employee", "client").order_by("-received_at")
    qs = qs.filter(received_at__gte=timezone.now() - timedelta(hours=hours))
    if assignment_only:
        qs = qs.filter(is_assignment=True)
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if client_id:
        qs = qs.filter(client_id=client_id)

    employees = Employee.objects.all()
    clients = Client.objects.all()

    return render(request, "core/dashboard.html", {
        "messages": qs[:500],
        "employees": employees,
        "clients": clients,
        "filters": {"hours": hours, "assignment": assignment_only, "employee": employee_id, "client": client_id},
    })

@login_required
def message_modal(request, pk):
    msg = get_object_or_404(Message.objects.select_related("employee", "client"), pk=pk)
    return render(request, "core/partials/message_modal.html", {"m": msg})

@login_required
def mappings(request):
    return render(request, "core/mappings.html", {"items": SenderMapping.objects.select_related("client").all(), "clients": Client.objects.all()})

@login_required
def create_mapping(request):
    if request.method == "POST":
        client_id = request.POST.get("client")
        domain = request.POST.get("domain", "")
        email = request.POST.get("email", "")
        subject_pattern = request.POST.get("subject_pattern", "")
        SenderMapping.objects.create(client_id=client_id, domain=domain, email=email, subject_pattern=subject_pattern)
        return redirect("mappings")
    return HttpResponse(status=405)

@login_required
def delete_mapping(request, pk):
    if request.method == "POST":
        SenderMapping.objects.filter(pk=pk).delete()
        return redirect("mappings")
    return HttpResponse(status=405)

@login_required
def employees(request):
    return render(request, "core/employees.html", {"items": Employee.objects.all()})

@login_required
def clients(request):
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        name = (request.POST.get("name") or "").strip()
        if not code or not name:
            messages.error(request, "Both Code and Name are required.")
            return redirect("clients")
        obj, created = Client.objects.get_or_create(code=code, defaults={"name": name})
        if not created:
            messages.warning(request, f"Client with code {code} already exists.")
        else:
            messages.success(request, f"Client {name} added.")
        return redirect("clients")

    items = Client.objects.order_by("code")
    return render(request, "core/clients.html", {"items": items})


# DEV: seed demo data quickly
@login_required
def seed_demo_view(request):
    if not request.user.is_superuser:
        return HttpResponse("Forbidden", status=403)
    from django.contrib.auth.models import User
    from .models import Employee, Client, EmployeeClient, Message, SenderMapping
    from datetime import datetime, timedelta, timezone as tz

    # Users & employees
    boss, _ = User.objects.get_or_create(username="boss", defaults={"is_staff": True, "is_superuser": True})
    e1u, _ = User.objects.get_or_create(username="alice")
    e2u, _ = User.objects.get_or_create(username="bob")
    e1, _ = Employee.objects.get_or_create(user=e1u, defaults={"display_name": "Alice", "primary_email": "alice@acme.com"})
    e2, _ = Employee.objects.get_or_create(user=e2u, defaults={"display_name": "Bob", "primary_email": "bob@acme.com"})

    # Clients
    c1, _ = Client.objects.get_or_create(code="C-13", defaults={"name": "Nova Labs"})
    c2, _ = Client.objects.get_or_create(code="C-05", defaults={"name": "Orion Foods"})

    # Links
    from .models import EmployeeClient
    EmployeeClient.objects.get_or_create(employee=e1, client=c1)
    EmployeeClient.objects.get_or_create(employee=e2, client=c2)

    # Mappings
    SenderMapping.objects.get_or_create(client=c1, domain="novalabs.com")
    SenderMapping.objects.get_or_create(client=c2, subject_pattern="C-05")

    # Messages (sample)
    now = timezone.now()
    samples = [
        (e1, c1, "pm@novalabs.com", "Kickoff: next project for C-13", "Please start the onboarding; deadline by July 22"),
        (e1, None, "news@digest.com", "Weekly newsletter", "Roundup of updates"),
        (e2, c2, "sam@orionfoods.com", "PO attached for C-05", "Purchase order attached. Due by Aug 3"),
    ]
    for i, (emp, client, sender, subj, snip) in enumerate(samples, start=1):
        is_assign, tags = detect_assignment(subj, snip)
        Message.objects.get_or_create(
            provider_msg_id=f"demo-{i}",
            defaults={
                "employee": emp,
                "client": client,
                "sender": sender,
                "subject": subj,
                "snippet": snip,
                "received_at": now - timedelta(hours=i),
                "is_assignment": is_assign,
                "tags": tags,
            },
        )
    return redirect("dashboard")



























@admin_required
def admin_dashboard(request):
    """
    /admin/dashboard - shows onboarding code (masked), employees list with approve toggle.
    """
    # For simplicity, assume a single Org owned by the first admin.
    # In multi-org setups, tie Org to request.user.
    org = Org.objects.order_by("id").first()
    employees = Employee.objects.select_related("user", "org").order_by("display_name", "user__username")

    masked = "•" * (len(org.special_code) - 4) + org.special_code[-4:] if org and org.special_code else ""
    return render(request, "core/onboarding.html", {
        "org": org,
        "employees": employees,
        "masked_code": masked,
    })

@admin_required
@require_http_methods(["POST"])
def admin_code_reveal(request):
    
    org = Org.objects.order_by("id").first()
    return render(request, "core/partials/admin_code_value.html", {"value": org.special_code})

@admin_required
@require_http_methods(["POST"])
def admin_code_regen(request):
    org = Org.objects.order_by("id").first()
    org.rotate_code()
    messages.success(request, "Admin code regenerated. Share the new code with employees.")
    return redirect("dashboard")

@admin_required
@require_http_methods(["POST"])
def admin_employee_approve(request, employee_id: int):
    emp = get_object_or_404(Employee, id=employee_id)
    emp.approved = True
    emp.save(update_fields=["approved"])
    messages.success(request, f"{emp.display_name} approved.")
    return redirect("dashboard")