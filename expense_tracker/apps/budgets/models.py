from django.conf import settings
from django.db import models

from apps.expenses.models import Category


class Budget(models.Model):
    PERIOD_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="budgets",
        help_text="Leave blank for an overall budget across all categories.",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="monthly")
    alert_threshold = models.IntegerField(
        default=80,
        help_text="Percentage of budget at which to trigger an alert email.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "category", "period")

    def __str__(self):
        cat = self.category.name if self.category else "All"
        return f"{self.user.email} — {cat} {self.period} budget ({self.amount})"
