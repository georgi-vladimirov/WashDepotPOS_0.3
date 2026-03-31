from django.urls import path
from . import views

app_name = "expences"
urlpatterns = [
    path("", views.ExpencesOverview.as_view(), name="overview"),
    path("add/", views.AddExpence.as_view(), name="add"),
    path("delete/<int:pk>/", views.DeleteExpence.as_view(), name="delete"),
]