import calendar
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from core.models import Location
from core.selectors import get_first_location_by_user
from .models import CalendarEvent


def get_last_cal_event_by_user(*, user: AbstractUser) -> CalendarEvent | None:
    """Return the most recent CalendarEvent for the user's first active location."""
    location = get_first_location_by_user(user=user)
    if location is None:
        return None
    return CalendarEvent.objects.filter(location=location).order_by("-date").first()


def get_cal_event_by_id(*, cal_event_id: str) -> CalendarEvent | None:
    """Return a CalendarEvent by primary key, or None if not found."""
    return CalendarEvent.objects.filter(pk=cal_event_id).first()


def get_cal_events_for_month(*, location: Location, year: int, month: int) -> dict:
    """Return a dict mapping day number to event info for the given location and month."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    cal_events = CalendarEvent.objects.filter(
        date__range=(first_day, last_day), location=location
    )
    return {
        event.date.day: {
            "id": event.pk,
            "date": event.date,
            "active": event.is_active,
        }
        for event in cal_events
    }


def get_cal_events_for_period(*, cal_event: CalendarEvent) -> QuerySet[CalendarEvent]:
    """Return all CalendarEvents for the same month and location as the given event, ordered by date."""
    first_day: date = cal_event.date.replace(day=1)
    last_day: date = cal_event.date.replace(
        day=calendar.monthrange(cal_event.date.year, cal_event.date.month)[1]
    )
    return CalendarEvent.objects.filter(
        date__range=(first_day, last_day), location=cal_event.location
    ).order_by("date")
