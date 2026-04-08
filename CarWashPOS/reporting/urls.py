from django.urls import path
from . import views

app_name = "reporting"
urlpatterns = [
    path("", views.MonthlyReport.as_view(), name="monthly_report"),

]