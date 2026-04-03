import django_filters

from .models import Expense


class ExpenseFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category__id")
    recurrence = django_filters.CharFilter(field_name="recurrence", lookup_expr="exact")
    currency = django_filters.CharFilter(field_name="currency", lookup_expr="iexact")

    class Meta:
        model = Expense
        fields = ["date_from", "date_to", "min_amount", "max_amount", "category", "recurrence", "currency"]
