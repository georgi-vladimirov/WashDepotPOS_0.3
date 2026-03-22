from django.db.models import QuerySet
from .models import Transaction
from core.models import CalendarEvent

def get_trans_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet:
    """Return all Transactions for the given CalendarEvent."""
    return Transaction.objects.filter(date=cal_event).select_related("sale", "employee", "date")
