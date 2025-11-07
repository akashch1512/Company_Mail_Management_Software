# accounts/services.py
from django.contrib.auth.models import User
from core.models import Org, Employee

def get_org_by_code(code: str) -> Org | None:
    try:
        return Org.objects.get(special_code=code)
    except Org.DoesNotExist:
        return None

def create_or_attach_employee(*, org: Org, google_email: str, display_name: str) -> Employee:
    # Use google_email as username if not existing
    user, _ = User.objects.get_or_create(
        username=google_email.lower(),
        defaults={"email": google_email, "first_name": display_name[:30]},
    )
    emp, created = Employee.objects.get_or_create(
        user=user,
        defaults={"org": org, "display_name": display_name or google_email, "primary_email": google_email, "approved": False},
    )
    if not created:
        # ensure org + email are set
        if emp.org_id != org.id:
            emp.org = org
        if not emp.primary_email:
            emp.primary_email = google_email
        if not emp.display_name:
            emp.display_name = display_name or google_email
        emp.save()
    return emp
