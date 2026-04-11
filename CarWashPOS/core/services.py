from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from typing import cast
import logging

from cal_app.selectors import get_cal_event_by_id, get_last_cal_event_by_user

logger = logging.getLogger("core.services")


def sync_cal_event_session(*, request: HttpRequest) -> None:
    """Ensures the session contains a valid cal_event_id, location and date."""
    cal_event_id = request.session.get("cal_event_id")

    if not cal_event_id:
        user = cast(AbstractUser, request.user)
        cal_event = get_last_cal_event_by_user(user=user)
        cal_event_id = cal_event.pk if cal_event else ""
        request.session["cal_event_id"] = cal_event_id
    else:
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)

    request.session["location"] = cal_event.location.name if cal_event else ""
    request.session["date"] = cal_event.date.isoformat() if cal_event else ""
