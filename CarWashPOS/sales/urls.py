from django.urls import path
from . import views

app_name = "sales"  # namespace for the app
urlpatterns = [
    path("sales/", views.SalesOverview.as_view(), name="sales_overview"),
    path("add-sale/", views.AddSale.as_view(), name="add_sale"),
]