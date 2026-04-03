from datetime import date

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsOwner
from apps.expenses.models import Expense

from .models import Budget
from .serializers import BudgetSerializer, BudgetStatusSerializer
from .utils import get_period_dates


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related("category")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="status")
    def status(self, request, pk=None):
        budget = self.get_object()
        period_start, period_end = get_period_dates(budget.period)

        qs = Expense.objects.filter(
            user=request.user,
            date__gte=period_start,
            date__lte=period_end,
        )
        if budget.category:
            qs = qs.filter(category=budget.category)

        total_spent = qs.aggregate(total=Sum("amount"))["total"] or 0
        remaining = budget.amount - total_spent
        utilization_pct = (float(total_spent) / float(budget.amount)) * 100 if budget.amount else 0

        data = {
            "budget_id": budget.id,
            "budget_amount": budget.amount,
            "period": budget.period,
            "total_spent": total_spent,
            "remaining": remaining,
            "utilization_pct": round(utilization_pct, 2),
            "alert_threshold": budget.alert_threshold,
            "is_over_budget": total_spent > budget.amount,
            "period_start": period_start,
            "period_end": period_end,
        }
        serializer = BudgetStatusSerializer(data)
        return Response(serializer.data)
