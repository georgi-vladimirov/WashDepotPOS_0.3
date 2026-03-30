from .models import Expence
from core.models import CalendarEvent
from django.db.models import QuerySet
from transactions.models import Transaction, TranType, Origin, PaymentMethod


def create_tran_for_expence(*, expence: Expence) -> Transaction:
    trasaction: Transaction = Transaction.objects.create(
        date=expence.date,
        type=TranType.OUT,
        origin = Origin.COST,
        amount=expence.amount,
        payment_method=PaymentMethod.CASH,
        details=expence.name,
    )
    return trasaction

def save_expence(*, expence: Expence) -> None:
    expence.save()
    transaction = create_tran_for_expence(expence=expence)
    transaction.save()
