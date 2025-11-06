from django.contrib import admin
from .models import Employee, Client, EmployeeClient, SenderMapping, Message


admin.site.register(Employee)
admin.site.register(Client)
admin.site.register(EmployeeClient)
admin.site.register(SenderMapping)
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "employee", "client", "received_at", "is_assignment")
    list_filter = ("is_assignment", "employee", "client")
    search_fields = ("subject", "sender")