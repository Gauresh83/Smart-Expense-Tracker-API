from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("users/", include("apps.accounts.user_urls")),
    path("expenses/", include("apps.expenses.urls")),
    path("categories/", include("apps.expenses.category_urls")),
    path("budgets/", include("apps.budgets.urls")),
    path("analytics/", include("apps.analytics.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
