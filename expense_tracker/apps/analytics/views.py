from datetime import date, timedelta
import calendar

from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.expenses.models import Expense
from apps.accounts.models import User


def _parse_period_range(period: str):
    today = date.today()
    if period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == "month":
        start = today.replace(day=1)
        end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    elif period == "year":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:
        start = today.replace(day=1)
        end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return start, end


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get("period", "month")
        start, end = _parse_period_range(period)
        user = request.user

        qs = Expense.objects.filter(user=user, date__gte=start, date__lte=end)
        agg = qs.aggregate(
            total_spent=Sum("amount"),
            expense_count=Count("id"),
            avg_expense=Avg("amount"),
        )

        # Top category
        top_cat = (
            qs.values("category__id", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
            .first()
        )

        return Response({
            "period": period,
            "start_date": start,
            "end_date": end,
            "total_spent": agg["total_spent"] or 0,
            "expense_count": agg["expense_count"] or 0,
            "avg_expense": round(float(agg["avg_expense"] or 0), 2),
            "currency": user.currency,
            "budget_limit": user.monthly_budget,
            "budget_utilization_pct": (
                round(
                    float(agg["total_spent"] or 0) / float(user.monthly_budget) * 100, 2
                )
                if user.monthly_budget else None
            ),
            "top_category": {
                "id": top_cat["category__id"],
                "name": top_cat["category__name"],
                "total": top_cat["total"],
            } if top_cat else None,
        })


class ByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        qs = Expense.objects.filter(user=request.user)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        breakdown = (
            qs.values("category__id", "category__name", "category__color")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        total = sum(item["total"] for item in breakdown if item["total"])

        return Response({
            "date_from": date_from,
            "date_to": date_to,
            "total": total,
            "breakdown": [
                {
                    "category_id": item["category__id"],
                    "category_name": item["category__name"] or "Uncategorized",
                    "color": item["category__color"],
                    "total": item["total"],
                    "count": item["count"],
                    "pct": round(float(item["total"]) / float(total) * 100, 2) if total else 0,
                }
                for item in breakdown
            ],
        })


class TrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        months = int(request.query_params.get("months", 6))
        today = date.today()
        start = (today.replace(day=1) - timedelta(days=months * 28)).replace(day=1)

        data = (
            Expense.objects.filter(user=request.user, date__gte=start)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        return Response({
            "months": months,
            "trends": [
                {
                    "month": item["month"].strftime("%Y-%m"),
                    "total": item["total"],
                    "count": item["count"],
                }
                for item in data
            ],
        })


class TopExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        period = request.query_params.get("period", "month")
        start, end = _parse_period_range(period)

        expenses = (
            Expense.objects.filter(user=request.user, date__gte=start, date__lte=end)
            .select_related("category")
            .order_by("-amount")[:limit]
        )

        from apps.expenses.serializers import ExpenseSerializer
        return Response({
            "period": period,
            "limit": limit,
            "expenses": ExpenseSerializer(expenses, many=True, context={"request": request}).data,
        })
