from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = (
            "id", "category", "amount", "period",
            "alert_threshold", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_alert_threshold(self, value):
        if not (1 <= value <= 100):
            raise serializers.ValidationError("Alert threshold must be between 1 and 100.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value


class BudgetStatusSerializer(serializers.Serializer):
    budget_id = serializers.IntegerField()
    budget_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    period = serializers.CharField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
    utilization_pct = serializers.FloatField()
    alert_threshold = serializers.IntegerField()
    is_over_budget = serializers.BooleanField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()
