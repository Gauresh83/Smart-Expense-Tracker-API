from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount", "period", "alert_threshold")
    list_filter = ("period",)
    search_fields = ("user__email",)
