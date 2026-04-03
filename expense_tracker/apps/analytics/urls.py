from django.urls import path
from .views import SummaryView, ByCategoryView, TrendsView, TopExpensesView

urlpatterns = [
    path("summary/", SummaryView.as_view(), name="analytics-summary"),
    path("by-category/", ByCategoryView.as_view(), name="analytics-by-category"),
    path("trends/", TrendsView.as_view(), name="analytics-trends"),
    path("top-expenses/", TopExpensesView.as_view(), name="analytics-top-expenses"),
]
