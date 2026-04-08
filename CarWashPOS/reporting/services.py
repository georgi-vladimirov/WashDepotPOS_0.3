from sales.models import Sale, CartItem
from transactions.models import Transaction, Origin
from transactions.services import daily_report_calculate
from transactions.selectors import get_trans_for_location_and_date
from core.models import CalendarEvent, Location
from .dates import get_dates_for_month
from django.db.models import QuerySet, Count, Sum, F, Q
from datetime import date


def get_data_for_monthly_report(*, cal_event: CalendarEvent, year: int, month: int):
    """Return aggregated sales, cart items and transaction data for the given location, year and month."""

    location = cal_event.location

    sales_data = (
        Sale.objects.filter(
            date__location=location,
            date__date__year=year,
            date__date__month=month,
        )
        .annotate(cal_date=F("date__date"))
        .values("cal_date", "vehicle_type__name")
        .annotate(count_cars=Count("id"), count_subscribers=Count("subscriber"))
        .order_by("cal_date", "vehicle_type__name")
    )

    cartItems_data = (
        CartItem.objects.filter(
            cart__sale__date__location=location,
            cart__sale__date__date__year=year,
            cart__sale__date__date__month=month,
        )
        .annotate(cal_date=F("cart__sale__date__date"))
        .values("cal_date", "service__service_type__name")
        .annotate(amount=Sum("amount"))
        .order_by("cal_date", "service__service_type__name")
    )

    transactions_base = Transaction.objects.filter(
        date__location=location,
        date__date__year=year,
        date__date__month=month,
    )

    transactions_data = (
        transactions_base.filter(origin=Origin.INCOME)
        .annotate(cal_date=F("date__date"))
        .values("cal_date", "payment_method")
        .annotate(amount=Sum("amount"))
        .order_by("cal_date", "payment_method")
    )

    costs_data = (
        transactions_base.filter(origin=Origin.COST)
        .annotate(cal_date=F("date__date"))
        .values("cal_date")
        .annotate(amount=Sum("amount"))
        .order_by("cal_date")
    )

    salaries_data = (
        transactions_base.filter(origin=Origin.SALARY)
        .annotate(cal_date=F("date__date"))
        .values("cal_date")
        .annotate(amount=Sum("amount"))
        .order_by("cal_date")
    )

    bonus_data = (
        transactions_base.filter(origin=Origin.BONUS)
        .annotate(cal_date=F("date__date"))
        .values("cal_date")
        .annotate(amount=Sum("amount"))
        .order_by("cal_date")
    )

    return (
        sales_data,
        transactions_data,
        cartItems_data,
        costs_data,
        salaries_data,
        bonus_data,
    )


def monthly_report_pivot(
    *,
    year: int,
    month: int,
    location: Location,
    sales_data: QuerySet,
    transactions_data: QuerySet,
    cartItems_data: QuerySet,
    costs_data: QuerySet,
    salaries_data: QuerySet,
    bonus_data: QuerySet,
) -> tuple[list[dict], dict]:
    """
    Pivot all report querysets into a list of day rows.

    Returns:
        rows    — list of dicts, one per day in the month.
        columns — dict of dynamic column name lists for use in template headers:
                  {"vehicle_types": [...], "service_types": [...], "payment_methods": [...]}
    """
    # Evaluate querysets once to allow two-pass iteration without extra DB hits
    sales_data_list = list(sales_data)
    transactions_data_list = list(transactions_data)
    cartItems_data_list = list(cartItems_data)
    costs_data_list = list(costs_data)
    salaries_data_list = list(salaries_data)
    bonus_data_list = list(bonus_data)

    # Collect dynamic column names from the data
    vehicle_types = sorted({row["vehicle_type__name"] for row in sales_data_list})
    service_types = sorted(
        {row["service__service_type__name"] for row in cartItems_data_list}
    )
    payment_methods = sorted({row["payment_method"] for row in transactions_data_list})

    # Build report skeleton — one entry per calendar day, all values default to None / 0
    all_dates = get_dates_for_month(year, month)
    report: dict[date, dict] = {}
    for d in all_dates:
        report[d] = {
            "date": d,
            "total_cars": 0,
            "total_subscribers": 0,
            "vehicle_types": {vt: None for vt in vehicle_types},
            "service_types": {st: None for st in service_types},
            "total_services": None,
            "payment_methods": {pm: None for pm in payment_methods},
            "total_payments": None,
            "costs": None,
            "salaries": None,
            "bonus": None,
            "cash_balance": None,
        }

    # --- fill vehicle type / car counts ---
    for row in sales_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["vehicle_types"][row["vehicle_type__name"]] = row["count_cars"]
            report[d]["total_cars"] += row["count_cars"]
            report[d]["total_subscribers"] += row["count_subscribers"]

    # --- fill service type revenue ---
    for row in cartItems_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["service_types"][row["service__service_type__name"]] = row[
                "amount"
            ]

    # --- compute total services per day ---
    for d, row in report.items():
        values = [v for v in row["service_types"].values() if v is not None]
        if values:
            row["total_services"] = sum(values)

    # --- fill payment method revenue ---
    for row in transactions_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["payment_methods"][row["payment_method"]] = row["amount"]

    # --- compute total payments per day ---
    for d, row in report.items():
        values = [v for v in row["payment_methods"].values() if v is not None]
        if values:
            row["total_payments"] = sum(values)

    # --- fill single-value per day datasets ---
    for row in costs_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["costs"] = row["amount"]

    for row in salaries_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["salaries"] = row["amount"]

    for row in bonus_data_list:
        d = row["cal_date"]
        if d in report:
            report[d]["bonus"] = row["amount"]

    for d, row in report.items():
        transactions = get_trans_for_location_and_date(location=location, date=d)
        cash_balance = daily_report_calculate(transactions_qs=transactions)
        report[d]["cash_balance"] = cash_balance

    # Extract cash_balance column structure from the first day that has data
    cash_balance_columns = []
    for row in report.values():
        if row["cash_balance"]:
            cash_balance_columns = [
                {
                    "key": key,
                    "label": val["label"],
                    "highlight": key in ("CASH_BALANCE", "POS_BALANCE"),
                    "bg_class": (
                        "table-info"
                        if key == "CASH_BALANCE"
                        else "table-warning"
                        if key == "POS_BALANCE"
                        else ""
                    ),
                }
                for key, val in row["cash_balance"].items()
            ]
            break

    columns = {
        "vehicle_types": vehicle_types,
        "service_types": service_types,
        "payment_methods": payment_methods,
        "cash_balance_columns": cash_balance_columns,
    }

    return list(report.values()), columns
