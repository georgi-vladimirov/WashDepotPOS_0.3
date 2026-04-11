from django.urls import path
from . import views

app_name = "cal_app"
urlpatterns = [
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path(
        "set-date-location/",
        views.SetDateLocationView.as_view(),
        name="set_date_location",
    ),
    path(
        "create-calendar-event/",
        views.CreateNewCalendarEventView.as_view(),
        name="create_calendar_event",
    ),
]
