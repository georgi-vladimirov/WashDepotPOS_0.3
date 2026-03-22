from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from typing import TypedDict
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import Transaction
from .filters import FILTERS



class AggregateData(TypedDict):
    """Type definition for aggregate data structure used in cash desk operations."""
    amount: Decimal
    order: int
    label: str | Promise


def daily_report_calculate(transactions_qs, filters=FILTERS) -> dict[str, AggregateData]:
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
