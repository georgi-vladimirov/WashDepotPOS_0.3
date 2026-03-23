from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import logging
from typing import TypedDict
from django.db.models import Sum
from django.db.models.functions import Coalesce
from sales.models import Sale
from sales.selectors import get_sale_unpaid_amount
from core.models import CalendarEvent
from .models import Transaction
from .filters import FILTERS
from .selectors import get_trans_amount_by_sale

logger = logging.getLogger("transactions.services")


class AggregateData(TypedDict):
    """Type definition for aggregate data structure used in cash desk operations."""
    amount: Decimal
    order: int
    label: str | Promise


def daily_report_calculate(*, transactions_qs, filters=FILTERS) -> dict[str, AggregateData]:
    """Calculate daily report aggregates from transaction queryset."""

    # Calculate all aggregates
    aggregates: dict[str, AggregateData] = {}
    cash_at_hand = Decimal(0)
    cash_balance = Decimal(0)
    pos_balance = Decimal(0)
    for key, defn in filters.items():
        result = transactions_qs.filter(**defn["filter_kwargs"]).aggregate(total=Coalesce(Sum("amount"), Decimal(0)))
        aggregates[key] = {"amount": result["total"], "order": defn["order"], "label": defn["label"]}
        if key in ["START", "DEPOSIT", "INCOME_CASH", "WITHDRAW", "COSTS", "SALARIES", "BONUS", "ADVANCES"]:
            cash_at_hand += result["total"]

    cash_balance = cash_at_hand - aggregates["END"]["amount"]
    pos_balance = aggregates["INCOME_CARD"]["amount"] - aggregates["POS_RECEIPT"]["amount"]

    aggregates["CASH_AT_HAND"] = {"amount": cash_at_hand, "order": 9, "label": _("Cash at Hand")}
    aggregates["CASH_BALANCE"] = {"amount": cash_balance, "order": 11, "label": _("Cash Balance")}
    aggregates["POS_BALANCE"] = {"amount": pos_balance, "order": 13, "label": _("POS Balance")}

    # Sort aggregates by order
    aggregates = dict(sorted(aggregates.items(), key=lambda item: item[1]["order"]))

    return aggregates


def sale_accepts_transaction(*, sale: Sale, transaction: Transaction) -> bool:
    sale_unpaid_amount = get_sale_unpaid_amount(sale=sale)
    trans_amount = get_trans_amount_by_sale(sale=sale)
    return sale_unpaid_amount >= trans_amount


def process_sale_payment(*, sale: Sale, transaction: Transaction) -> bool:
    if not sale_accepts_transaction(sale=sale, transaction=transaction):
        logger.warning("Transaction: %s does not cover sale: %s", transaction, sale)
        return False
    return True


def transaction_save(*, transaction: Transaction) -> tuple[Transaction, bool]:
    sale: Sale = transaction.sale
    if sale:
        if process_sale_payment(sale=sale, transaction=transaction):
            transaction.save()
            logger.info("Transaction: %s for sale: %s saved.", transaction, sale)
            return transaction, True
        else:
            return transaction, False

    transaction.save()
    return transaction, True
