from django.urls import path
from . import views

app_name = "core"  # namespace for the app
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path("set-date-location/", views.SetDateLocationView.as_view(), name="set_date_location"),
    path("create-calendar-event/", views.CreateNewCalendarEventView.as_view(), name="create_calendar_event"),
]
