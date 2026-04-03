from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "currency", "is_active", "created_at")
    list_filter = ("is_active", "currency")
    search_fields = ("email", "username")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("currency", "timezone", "monthly_budget")}),
    )
