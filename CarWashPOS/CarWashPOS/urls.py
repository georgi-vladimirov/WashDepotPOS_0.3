from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("", include("cal_app.urls")),
    path("", include("sales.urls")),
    path("transactions/", include("transactions.urls")),
    path("expences/", include("expences.urls")),
    path("salaries/", include("salaries.urls")),
    path("reporting/", include("reporting.urls")),
)


if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]
