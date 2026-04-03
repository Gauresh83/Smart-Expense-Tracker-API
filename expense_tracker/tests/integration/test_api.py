import pytest
import decimal
import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import UserFactory, CategoryFactory, ExpenseFactory


def get_auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
class TestAuthEndpoints:
    def test_register(self):
        client = APIClient()
        payload = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = client.post("/api/v1/auth/register/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["email"] == "new@example.com"

    def test_register_password_mismatch(self):
        client = APIClient()
        payload = {
            "email": "x@example.com",
            "username": "xuser",
            "password": "StrongPass123!",
            "password2": "WrongPass123!",
        }
        response = client.post("/api/v1/auth/register/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login(self):
        user = UserFactory()
        client = APIClient()
        response = client.post("/api/v1/auth/login/", {
            "email": user.email,
            "password": "TestPass123!",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_logout(self):
        user = UserFactory()
        client = get_auth_client(user)
        refresh = RefreshToken.for_user(user)
        response = client.post("/api/v1/auth/logout/", {"refresh": str(refresh)})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestExpenseEndpoints:
    def test_list_expenses_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/expenses/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_expenses(self):
        user = UserFactory()
        ExpenseFactory.create_batch(3, user=user)
        client = get_auth_client(user)
        response = client.get("/api/v1/expenses/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_user_sees_only_own_expenses(self):
        user_a = UserFactory()
        user_b = UserFactory()
        ExpenseFactory.create_batch(2, user=user_a)
        ExpenseFactory.create_batch(5, user=user_b)
        client = get_auth_client(user_a)
        response = client.get("/api/v1/expenses/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_create_expense(self):
        user = UserFactory()
        category = CategoryFactory(user=user)
        client = get_auth_client(user)
        payload = {
            "amount": "75.00",
            "currency": "USD",
            "category_id": category.id,
            "description": "Team lunch",
            "date": str(datetime.date.today()),
            "recurrence": "none",
        }
        response = client.post("/api/v1/expenses/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "75.00"

    def test_create_expense_negative_amount(self):
        user = UserFactory()
        client = get_auth_client(user)
        payload = {
            "amount": "-10.00",
            "currency": "USD",
            "date": str(datetime.date.today()),
        }
        response = client.post("/api/v1/expenses/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_own_expense(self):
        user = UserFactory()
        expense = ExpenseFactory(user=user)
        client = get_auth_client(user)
        response = client.get(f"/api/v1/expenses/{expense.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == expense.id

    def test_cannot_access_other_users_expense(self):
        owner = UserFactory()
        attacker = UserFactory()
        expense = ExpenseFactory(user=owner)
        client = get_auth_client(attacker)
        response = client.get(f"/api/v1/expenses/{expense.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_expense(self):
        user = UserFactory()
        expense = ExpenseFactory(user=user, description="Old desc")
        client = get_auth_client(user)
        response = client.patch(
            f"/api/v1/expenses/{expense.id}/",
            {"description": "New desc"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_expense(self):
        user = UserFactory()
        expense = ExpenseFactory(user=user)
        client = get_auth_client(user)
        response = client.delete(f"/api/v1/expenses/{expense.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_expenses_by_date(self):
        user = UserFactory()
        ExpenseFactory(user=user, date=datetime.date(2025, 1, 10))
        ExpenseFactory(user=user, date=datetime.date(2025, 6, 15))
        client = get_auth_client(user)
        response = client.get("/api/v1/expenses/", {"date_from": "2025-06-01", "date_to": "2025-06-30"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_bulk_create_expenses(self):
        user = UserFactory()
        client = get_auth_client(user)
        payload = {
            "expenses": [
                {"amount": "10.00", "currency": "USD", "date": str(datetime.date.today()), "recurrence": "none"},
                {"amount": "20.00", "currency": "USD", "date": str(datetime.date.today()), "recurrence": "none"},
            ]
        }
        response = client.post("/api/v1/expenses/bulk/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2

    def test_export_returns_task_id(self):
        user = UserFactory()
        client = get_auth_client(user)
        response = client.post("/api/v1/expenses/export/", {"format": "csv"}, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data


@pytest.mark.django_db
class TestCategoryEndpoints:
    def test_create_category(self):
        user = UserFactory()
        client = get_auth_client(user)
        response = client.post("/api/v1/categories/", {"name": "Travel", "color": "#ff0000"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_categories_own_only(self):
        user_a = UserFactory()
        user_b = UserFactory()
        CategoryFactory.create_batch(3, user=user_a)
        CategoryFactory.create_batch(2, user=user_b)
        client = get_auth_client(user_a)
        response = client.get("/api/v1/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3


@pytest.mark.django_db
class TestAnalyticsEndpoints:
    def test_summary(self):
        user = UserFactory()
        ExpenseFactory.create_batch(5, user=user, amount=decimal.Decimal("100.00"))
        client = get_auth_client(user)
        response = client.get("/api/v1/analytics/summary/", {"period": "month"})
        assert response.status_code == status.HTTP_200_OK
        assert "total_spent" in response.data

    def test_by_category(self):
        user = UserFactory()
        cat = CategoryFactory(user=user)
        ExpenseFactory.create_batch(3, user=user, category=cat)
        client = get_auth_client(user)
        response = client.get("/api/v1/analytics/by-category/")
        assert response.status_code == status.HTTP_200_OK
        assert "breakdown" in response.data

    def test_trends(self):
        user = UserFactory()
        client = get_auth_client(user)
        response = client.get("/api/v1/analytics/trends/", {"months": "3"})
        assert response.status_code == status.HTTP_200_OK
        assert "trends" in response.data

    def test_top_expenses(self):
        user = UserFactory()
        ExpenseFactory.create_batch(5, user=user)
        client = get_auth_client(user)
        response = client.get("/api/v1/analytics/top-expenses/", {"limit": "3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["expenses"]) <= 3
