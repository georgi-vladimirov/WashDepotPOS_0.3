from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import logging
from typing import Tuple, TypedDict
from django.db.models import Sum, aggregates
from django.db.models.functions import Coalesce
from sales.models import Sale
from sales.selectors import get_sale_unpaid_amount
from sales.services import set_sale_status
from core.models import CalendarEvent
from .models import Transaction, TranType, Origin
from .filters import FILTERS
from .selectors import get_cash_end_from_prev_cal_event, get_trans_by_cal_event

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
    aggregates["CASH_BALANCE"] = {"amount": cash_balance, "order": 10, "label": _("Cash Balance")}
    aggregates["POS_BALANCE"] = {"amount": pos_balance, "order": 13, "label": _("POS Balance")}

    # Sort aggregates by order
    aggregates = dict(sorted(aggregates.items(), key=lambda item: item[1]["order"]))

    return aggregates


def sale_accepts_transaction(*, sale: Sale, transaction: Transaction) -> bool:
    sale_unpaid_amount = get_sale_unpaid_amount(sale=sale)
    trans_amount = transaction.amount
    return sale_unpaid_amount >= trans_amount


def process_sale_payment(*, sale: Sale, transaction: Transaction) -> bool:
    if not sale_accepts_transaction(sale=sale, transaction=transaction):
        logger.warning("transaction_does_not_cover_sale", extra={"sale": sale.logger_data(), "transaction": transaction.logger_data()})
        return False
    return True


def process_transaction_START(*, transaction: Transaction) -> bool:
    cal_event = transaction.date
    last_end_trans = get_cash_end_from_prev_cal_event(cal_event=cal_event)
    if not last_end_trans:
        return True
    if transaction.amount == last_end_trans.amount:
        return True
    else:
        logger.warning("START_does_not_match_last_END", extra={"transaction": transaction.logger_data(), "last_end": last_end_trans.logger_data()})
        return False


def calculate_cash_balance(*, cal_event: CalendarEvent) -> Decimal:
    transactions_for_day = get_trans_by_cal_event(cal_event=cal_event)
    aggregates = daily_report_calculate(transactions_qs=transactions_for_day)
    cash_balance:Decimal = aggregates["CASH_BALANCE"]["amount"]
    return cash_balance


def process_transaction_END(*, transaction: Transaction) -> bool:
    cash_balance: Decimal = calculate_cash_balance(cal_event=transaction.date)
    if transaction.amount == cash_balance:
        return True
    else:
        logger.warning("END_does_not_match_cash_balance", extra={"transaction": transaction.logger_data(), "cash_balance": cash_balance})
        return False


def transaction_save(*, transaction: Transaction) -> tuple[Transaction, bool]:
    sale: Sale = transaction.sale
    if sale:
        if process_sale_payment(sale=sale, transaction=transaction):
            transaction.details = f"{sale.reg_number} | {sale.date.date.strftime('%d.%m.%Y')}"
            transaction.save()
            set_sale_status(sale=sale)
            logger.info("sale_payment_saved", extra={"sale": sale.logger_data(), "transaction": transaction.logger_data()})
            return transaction, True
        else:
            return transaction, False

    transaction.save()
    return transaction, True


def transaction_operation_save(*, transaction: Transaction) -> tuple[Transaction, bool]:
    process_result: tuple[Transaction, bool] = (transaction, False)

    if transaction.type == TranType.START:
        process_result = transaction, process_transaction_START(transaction=transaction)

    if transaction.type == TranType.END:
        process_result = transaction, process_transaction_END(transaction=transaction)

    if transaction.type == TranType.IN and transaction.origin == Origin.DEPOSIT:
        process_result = transaction, True

    if transaction.type == TranType.OUT and transaction.origin == Origin.WITHDRAW:
        process_result = transaction, True

    if transaction.type == TranType.POS and transaction.origin == Origin.BALANCE:
        process_result = transaction, True

    if process_result[1]:
        transaction.save()
        logger.info("transaction_saved", extra={"transaction": transaction.logger_data()})
        return process_result
    return process_result


def transaction_delete(*, transaction: Transaction) -> bool:
    transaction.delete()
    logger.info("transaction_deleted", extra={"transaction": transaction.logger_data()})
    return True