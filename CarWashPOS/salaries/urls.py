from django.urls import path
from . import views

app_name = "salaries"
urlpatterns = [
    path("", views.SalariesOverview.as_view(), name="salaries_overview"),
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("penalty/", views.PenaltyView.as_view(), name="penalty"),
]