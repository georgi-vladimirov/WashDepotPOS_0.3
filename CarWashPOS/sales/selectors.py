from .models import Sale
from core.models import CalendarEvent
from django.db.models import QuerySet


def get_sales_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet[Sale]:
    """Return a QuerySet of Sale objects for the given CalendarEvent."""
    return Sale.objects.filter(date=cal_event).select_related(
        "vehicle_type", "vehicle_brand", "subscriber", "cart", "worker", "manager"
    )
