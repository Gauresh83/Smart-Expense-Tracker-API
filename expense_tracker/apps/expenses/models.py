from django.conf import settings
from django.db import models


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default="")
    color = models.CharField(max_length=7, blank=True, default="#6366f1")  # hex
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class Expense(models.Model):
    RECURRENCE_CHOICES = [
        ("none", "None"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    description = models.TextField(blank=True, default="")
    date = models.DateField()
    receipt = models.ImageField(upload_to="receipts/%Y/%m/", null=True, blank=True)
    recurrence = models.CharField(
        max_length=10, choices=RECURRENCE_CHOICES, default="none"
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
            models.Index(fields=["user", "recurrence"]),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.amount} {self.currency} on {self.date}"
