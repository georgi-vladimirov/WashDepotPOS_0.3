from django.db.models import QuerySet, Sum, Q
from .models import Transaction, TranType
from core.models import Location
from cal_app.models import CalendarEvent
from cal_app.selectors import get_cal_events_for_period, get_cal_events_for_month
from decimal import Decimal
from datetime import date


def get_trans_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet[Transaction]:
    """Return all Transactions for the given CalendarEvent."""
    return Transaction.objects.filter(date=cal_event).select_related(
        "sale", "employee", "date"
    )


def get_trans_by_sale(*, sale) -> QuerySet[Transaction]:
    """Return all Transactions for the given Sale."""
    return Transaction.objects.filter(sale=sale).select_related("sale", "date")


def get_trans_amount_by_sale(*, sale) -> Decimal:
    """Return the total amount of all Transactions for the given Sale."""
    transactions: QuerySet[Transaction] = get_trans_by_sale(sale=sale)
    return transactions.aggregate(total=Sum("amount"))["total"] or Decimal(0)


def get_cash_end_from_prev_cal_event(*, cal_event: CalendarEvent) -> Transaction | None:
    """Return the cash end amount from the previous CalendarEvent."""
    prev_cal_event = (
        CalendarEvent.objects.filter(date__lt=cal_event.date).order_by("-date").first()
    )
    if not prev_cal_event:
        return None
    end_trans: Transaction | None = (
        get_trans_by_cal_event(cal_event=prev_cal_event)
        .filter(type=TranType.END)
        .first()
    )
    return end_trans


def get_tran_by_id(*, pk: int) -> Transaction | None:
    """Return the Transaction with the given primary key."""
    return Transaction.objects.filter(pk=pk).first()


def get_trans_for_period(*, cal_event: CalendarEvent) -> QuerySet[Transaction]:
    """Return a QuerySet of Transaction objects for the given CalendarEvent."""
    cal_events = get_cal_events_for_period(cal_event=cal_event)
    period_q = Q(date__in=cal_events)
    return Transaction.objects.filter(period_q)


def get_trans_for_location_and_date(
    *, location: Location, date: date
) -> QuerySet[Transaction]:
    """Return a QuerySet of Transaction objects for the given location and date."""
    filter = Q(date__date=date, date__location=location)
    return Transaction.objects.filter(filter)
