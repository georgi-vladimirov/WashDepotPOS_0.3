from .models import CalendarEvent, Location
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
import calendar
from datetime import date


def get_first_location_by_user(*, user: AbstractUser) -> Location | None:
    """Return the first active Location associated with the user's groups."""
    groups = user.groups.all()
    return Location.objects.filter(is_active=True, groups__group__in=groups).first()


def get_all_locations_by_user(*, user: AbstractUser) -> QuerySet[Location]:
    """Return all distinct active Locations associated with the user's groups."""
    groups = user.groups.all()
    return Location.objects.filter(is_active=True, groups__group__in=groups).distinct()


def get_location_by_id(*, location_id: str) -> Location | None:
    """Return a Location by primary key, or None if not found."""
    return Location.objects.filter(pk=location_id, is_active=True).first()


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
    cal_events = CalendarEvent.objects.filter(date__range=(first_day, last_day), location=location)
    return {
        event.date.day: {
            "id": event.pk,
            "date": event.date,
            "active": event.is_active,
        }
        for event in cal_events
    }
