from django.urls import path
from . import views

app_name = "sales"  # namespace for the app
urlpatterns = [
    path("sales/", views.SalesOverview.as_view(), name="sales_overview"),
    path("add-sale/", views.AddSale.as_view(), name="add_sale"),
    path("delete-sale/<int:sale_id>/", views.DeleteSale.as_view(), name="delete_sale"),
    path("add-cart/<int:sale_id>/", views.AddCart.as_view(), name="add_cart"),
    path("delete-cart/<int:cart_id>/", views.DeleteCart.as_view(), name="cart-delete"),
]
