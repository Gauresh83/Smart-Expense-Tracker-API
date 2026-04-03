import csv
import io

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsOwner
from apps.notifications.tasks import export_expenses_csv, check_budget_utilization

from .filters import ExpenseFilter
from .models import Expense, Category
from .serializers import (
    ExpenseSerializer,
    ExpenseDetailSerializer,
    BulkExpenseSerializer,
    CategorySerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = ExpenseFilter
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]
    search_fields = ["description", "metadata"]

    def get_queryset(self):
        return (
            Expense.objects.filter(user=self.request.user)
            .select_related("category")
            .only(
                "id", "amount", "currency", "description",
                "date", "recurrence", "created_at", "updated_at",
                "receipt", "category__id", "category__name",
                "category__color", "category__icon",
            )
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ExpenseDetailSerializer
        return ExpenseSerializer

    def perform_create(self, serializer):
        expense = serializer.save(user=self.request.user)
        if expense.category:
            check_budget_utilization.delay(self.request.user.id, expense.category.id)

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create(self, request):
        serializer = BulkExpenseSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        expenses_data = serializer.validated_data["expenses"]
        created = Expense.objects.bulk_create(
            [Expense(user=request.user, **data) for data in expenses_data]
        )
        return Response(
            ExpenseSerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="export")
    def export(self, request):
        fmt = request.data.get("format", "csv")
        filters = request.data.get("filters", {})
        task = export_expenses_csv.delay(
            user_id=request.user.id,
            filters=filters,
            fmt=fmt,
        )
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    ordering = ["name"]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
