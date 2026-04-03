import csv
import io
import logging
from datetime import date

from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: int, uid: str, token: str):
    """Send password reset email to user."""
    try:
        from apps.accounts.models import User
        user = User.objects.get(pk=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"
        send_mail(
            subject="Reset your Expense Tracker password",
            message=f"Click the link to reset your password: {reset_url}\n\nThis link expires in 24 hours.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Password reset email sent to %s", user.email)
    except Exception as exc:
        logger.error("Failed to send password reset email: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_budget_alert(self, user_id: int, budget_id: int, utilization_pct: float):
    """Fire when spend crosses the configured alert_threshold."""
    try:
        from apps.accounts.models import User
        from apps.budgets.models import Budget
        user = User.objects.get(pk=user_id)
        budget = Budget.objects.get(pk=budget_id)
        category_name = budget.category.name if budget.category else "Overall"
        send_mail(
            subject=f"Budget Alert: {category_name} at {utilization_pct:.1f}%",
            message=(
                f"Hi {user.username},\n\n"
                f"You have used {utilization_pct:.1f}% of your {budget.period} "
                f"{category_name} budget (limit: {budget.amount} {user.currency}).\n\n"
                f"Stay on track — review your expenses in the dashboard."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(
            "Budget alert sent to %s for budget %s (%.1f%%)",
            user.email, budget_id, utilization_pct
        )
    except Exception as exc:
        logger.error("Failed to send budget alert: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def check_budget_utilization(self, user_id: int, category_id: int):
    """Check if any budgets for this category need an alert email."""
    try:
        from apps.budgets.models import Budget
        from apps.budgets.utils import get_period_dates
        from apps.expenses.models import Expense

        budgets = Budget.objects.filter(
            user_id=user_id,
            category_id=category_id,
        )
        for budget in budgets:
            period_start, period_end = get_period_dates(budget.period)
            total_spent = Expense.objects.filter(
                user_id=user_id,
                category_id=category_id,
                date__gte=period_start,
                date__lte=period_end,
            ).aggregate(total=Sum("amount"))["total"] or 0

            utilization_pct = float(total_spent) / float(budget.amount) * 100
            if utilization_pct >= budget.alert_threshold:
                send_budget_alert.delay(user_id, budget.id, utilization_pct)
    except Exception as exc:
        logger.error("check_budget_utilization failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task
def check_all_budget_utilizations():
    """Periodic task: check budgets for all users (runs every hour)."""
    from apps.budgets.models import Budget
    from apps.budgets.utils import get_period_dates
    from apps.expenses.models import Expense

    for budget in Budget.objects.select_related("user", "category"):
        period_start, period_end = get_period_dates(budget.period)
        qs = Expense.objects.filter(
            user=budget.user,
            date__gte=period_start,
            date__lte=period_end,
        )
        if budget.category:
            qs = qs.filter(category=budget.category)

        total_spent = qs.aggregate(total=Sum("amount"))["total"] or 0
        utilization_pct = float(total_spent) / float(budget.amount) * 100
        if utilization_pct >= budget.alert_threshold:
            send_budget_alert.delay(budget.user.id, budget.id, utilization_pct)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def export_expenses_csv(self, user_id: int, filters: dict, fmt: str = "csv"):
    """On-demand export: generate CSV and email download link to user."""
    try:
        from apps.accounts.models import User
        from apps.expenses.models import Expense

        user = User.objects.get(pk=user_id)
        qs = Expense.objects.filter(user=user).select_related("category").order_by("-date")

        if filters.get("date_from"):
            qs = qs.filter(date__gte=filters["date_from"])
        if filters.get("date_to"):
            qs = qs.filter(date__lte=filters["date_to"])
        if filters.get("category"):
            qs = qs.filter(category_id=filters["category"])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Category", "Amount", "Currency", "Description", "Recurrence"])
        for exp in qs:
            writer.writerow([
                exp.date,
                exp.category.name if exp.category else "",
                exp.amount,
                exp.currency,
                exp.description,
                exp.recurrence,
            ])

        csv_content = output.getvalue()
        send_mail(
            subject="Your Expense Export is Ready",
            message=f"Hi {user.username},\n\nPlease find your expense export attached.\n\n---\n{csv_content[:500]}...",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Expense export sent to %s", user.email)
    except Exception as exc:
        logger.error("export_expenses_csv failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task
def generate_monthly_reports_for_all_users():
    """Celery Beat: runs on the 1st of each month at 08:00 UTC."""
    from apps.accounts.models import User
    for user in User.objects.filter(is_active=True):
        generate_monthly_report_for_user.delay(user.id)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_monthly_report_for_user(self, user_id: int):
    """Generate and email a monthly summary report for a single user."""
    try:
        from apps.accounts.models import User
        from apps.expenses.models import Expense

        user = User.objects.get(pk=user_id)
        today = date.today()
        # Report covers the previous month
        if today.month == 1:
            year, month = today.year - 1, 12
        else:
            year, month = today.year, today.month - 1

        expenses = Expense.objects.filter(
            user=user,
            date__year=year,
            date__month=month,
        ).select_related("category")

        total = expenses.aggregate(total=Sum("amount"))["total"] or 0
        count = expenses.count()

        send_mail(
            subject=f"Your Monthly Expense Summary — {date(year, month, 1).strftime('%B %Y')}",
            message=(
                f"Hi {user.username},\n\n"
                f"Here's your expense summary for {date(year, month, 1).strftime('%B %Y')}:\n\n"
                f"  Total spent:   {total} {user.currency}\n"
                f"  Transactions:  {count}\n\n"
                f"Log in to see a full breakdown by category."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Monthly report sent to %s for %s/%s", user.email, year, month)
    except Exception as exc:
        logger.error("generate_monthly_report_for_user failed: %s", exc)
        raise self.retry(exc=exc)
