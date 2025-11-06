from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    display_name = models.CharField(max_length=120)
    primary_email = models.EmailField(blank=True)
    def __str__(self):
        return self.display_name

class Client(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    def __str__(self):
        return f"{self.code} – {self.name}"


class EmployeeClient(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    class Meta:
        unique_together = ("employee", "client")

class SenderMapping(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    domain = models.CharField(max_length=120, blank=True)
    email = models.CharField(max_length=200, blank=True)
    subject_pattern = models.CharField(max_length=200, blank=True)
    def __str__(self):
        target = self.email or self.domain or self.subject_pattern
        return f"{self.client.name} ← {target}"
    

class Message(models.Model):
    provider_msg_id = models.CharField(max_length=255, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    sender = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    snippet = models.TextField(blank=True)
    received_at = models.DateTimeField()
    tags = models.JSONField(default=list, blank=True)
    is_assignment = models.BooleanField(default=False)
    class Meta:
        indexes = [models.Index(fields=["employee", "client", "received_at"])]
    def __str__(self):
        return self.subject[:60]