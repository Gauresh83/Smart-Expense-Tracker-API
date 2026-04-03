import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
import decimal
import datetime

from apps.accounts.models import User
from apps.expenses.models import Category, Expense
from apps.budgets.models import Budget


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    currency = "USD"
    timezone = "UTC"
    is_active = True


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    color = "#6366f1"
    icon = "tag"
    is_default = False


class ExpenseFactory(DjangoModelFactory):
    class Meta:
        model = Expense

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    amount = factory.LazyFunction(lambda: decimal.Decimal("49.99"))
    currency = "USD"
    description = factory.Faker("sentence", nb_words=4)
    date = factory.LazyFunction(datetime.date.today)
    recurrence = "none"
    metadata = factory.LazyFunction(dict)


class BudgetFactory(DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    amount = decimal.Decimal("500.00")
    period = "monthly"
    alert_threshold = 80
