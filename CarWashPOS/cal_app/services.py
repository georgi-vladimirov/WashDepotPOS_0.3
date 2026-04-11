import logging
from datetime import datetime

from django.http import Http404

from core.selectors import get_location_by_id
from .models import CalendarEvent

logger = logging.getLogger("cal_app.services")


def calendar_event_create(date_str: str, location_str: str) -> CalendarEvent:
    """Creates and returns a new CalendarEvent for the given date and location."""
    location = get_location_by_id(location_id=location_str)
    if not location:
        raise Http404(f"Location not found: {location_str}")
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    cal_event = CalendarEvent(date=date, location=location, is_active=True)
    cal_event.save()
    logger.info(
        "calendar_event_created", extra={"location_id": location.name, "date": date_str}
    )
    return cal_event
