from .models import Expence
from core.models import CalendarEvent
from django.db.models import QuerySet

def get_expences_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet:
    return Expence.objects.filter(date=cal_event)


def get_expence_by_id(*, pk: int) -> Expence | None:
    return Expence.objects.get(pk=pk)
