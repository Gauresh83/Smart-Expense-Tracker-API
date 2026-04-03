from rest_framework import serializers

from .models import Category, Expense


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "icon", "color", "is_default", "created_at")
        read_only_fields = ("id", "created_at")


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Expense
        fields = (
            "id", "category", "category_id", "amount", "currency",
            "description", "date", "receipt", "recurrence",
            "metadata", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["category_id"].queryset = Category.objects.filter(
                user=request.user
            )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class ExpenseDetailSerializer(ExpenseSerializer):
    """Full serializer for detail view — includes metadata JSONB."""
    class Meta(ExpenseSerializer.Meta):
        pass  # metadata already included in parent


class BulkExpenseSerializer(serializers.Serializer):
    expenses = ExpenseSerializer(many=True)

    def validate_expenses(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Bulk create is limited to 100 expenses.")
        return value
