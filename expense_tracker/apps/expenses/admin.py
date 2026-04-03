from django.contrib import admin
from .models import Expense, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "color", "is_default", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name", "user__email")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "category", "date", "recurrence")
    list_filter = ("recurrence", "currency")
    search_fields = ("description", "user__email")
    date_hierarchy = "date"
    ordering = ("-date",)
