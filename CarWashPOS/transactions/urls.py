from django.urls import path
from . import views

app_name = "transactions"
urlpatterns = [
    path("", views.TransactionsOverview.as_view(), name="trans_overview"),
    path("transactions/", views.TranSales.as_view(), name="transactions"),
    path("transactions/sales/<int:sale_id>", views.TranSales.as_view(), name="tran_sales"),
]
