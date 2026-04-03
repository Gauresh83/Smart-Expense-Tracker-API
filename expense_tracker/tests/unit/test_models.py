import pytest
import decimal
import datetime

from tests.factories import UserFactory, CategoryFactory, ExpenseFactory, BudgetFactory


@pytest.mark.django_db
class TestExpenseModel:
    def test_create_expense(self):
        expense = ExpenseFactory(amount=decimal.Decimal("99.99"))
        assert expense.pk is not None
        assert expense.amount == decimal.Decimal("99.99")
        assert expense.recurrence == "none"

    def test_expense_str(self):
        expense = ExpenseFactory()
        assert expense.user.email in str(expense)

    def test_expense_belongs_to_user(self):
        user = UserFactory()
        expense = ExpenseFactory(user=user)
        assert expense.user == user

    def test_expense_category_nullable(self):
        expense = ExpenseFactory(category=None)
        assert expense.category is None

    def test_expense_index_fields(self):
        """Ensure indexed fields exist on the model."""
        from apps.expenses.models import Expense
        field_names = [f.name for f in Expense._meta.get_fields()]
        assert "date" in field_names
        assert "category" in field_names


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = CategoryFactory(name="Food")
        assert cat.pk is not None
        assert cat.name == "Food"

    def test_unique_together_user_name(self):
        from django.db import IntegrityError
        user = UserFactory()
        CategoryFactory(user=user, name="Travel")
        with pytest.raises(IntegrityError):
            CategoryFactory(user=user, name="Travel")

    def test_different_users_same_name(self):
        """Two different users can have the same category name."""
        cat1 = CategoryFactory(name="Travel")
        cat2 = CategoryFactory(name="Travel")
        assert cat1.pk != cat2.pk


@pytest.mark.django_db
class TestBudgetModel:
    def test_create_budget(self):
        budget = BudgetFactory()
        assert budget.pk is not None
        assert budget.alert_threshold == 80

    def test_budget_str(self):
        budget = BudgetFactory()
        assert budget.user.email in str(budget)
