from django.db.models import QuerySet, Sum
from .models import Transaction, TranType
from core.models import CalendarEvent
from decimal import Decimal


def get_trans_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet[Transaction]:
    """Return all Transactions for the given CalendarEvent."""
    return Transaction.objects.filter(date=cal_event).select_related("sale", "employee", "date")


def get_trans_by_sale(*, sale) -> QuerySet[Transaction]:
    """Return all Transactions for the given Sale."""
    return Transaction.objects.filter(sale=sale).select_related("sale", "date")

def get_trans_amount_by_sale(*, sale) -> Decimal:
    """Return the total amount of all Transactions for the given Sale."""
    transactions: QuerySet[Transaction] = get_trans_by_sale(sale=sale)
    return transactions.aggregate(total=Sum("amount"))["total"] or Decimal(0)
    
def get_cash_end_from_prev_cal_event(*, cal_event: CalendarEvent) -> Transaction | None:
    """Return the cash end amount from the previous CalendarEvent."""
    prev_cal_event = CalendarEvent.objects.filter(date__lt=cal_event.date).order_by("-date").first()
    if not prev_cal_event:
        return None
    end_trans:Transaction | None = get_trans_by_cal_event(cal_event=prev_cal_event).filter(type = TranType.END).first()
    return end_trans
    
    
def get_tran_by_id(*, pk: int) -> Transaction | None:
    """Return the Transaction with the given primary key."""
    return Transaction.objects.filter(pk=pk).first()