from django.urls import path
from . import views

app_name = "transactions"
urlpatterns = [
    path("", views.TransactionsOverview.as_view(), name="trans_overview"),
]