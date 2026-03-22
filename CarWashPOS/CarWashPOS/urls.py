from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("", include("sales.urls")),
    path("transactions/", include("transactions.urls")),
)
