from django.db.models import QuerySet, Sum
from .models import Transaction
from core.models import CalendarEvent
from decimal import Decimal


def get_trans_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet:
    """Return all Transactions for the given CalendarEvent."""
    return Transaction.objects.filter(date=cal_event).select_related("sale", "employee", "date")


def get_trans_by_sale(*, sale) -> QuerySet[Transaction]:
    """Return all Transactions for the given Sale."""
    return Transaction.objects.filter(sale=sale).select_related("sale", "date")

def get_trans_amount_by_sale(*, sale) -> Decimal:
    """Return the total amount of all Transactions for the given Sale."""
    transactions: QuerySet[Transaction] = get_trans_by_sale(sale=sale)
    return transactions.aggregate(total=Sum("amount"))["total"] or Decimal(0)
