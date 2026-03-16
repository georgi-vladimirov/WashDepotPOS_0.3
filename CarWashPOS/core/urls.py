from django.urls import path
from . import views

app_name = 'core'   # namespace for the app
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]