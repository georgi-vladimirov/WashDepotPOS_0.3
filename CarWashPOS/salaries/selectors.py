from decimal import Decimal
from django.db.models import QuerySet, Q, F, Sum, DecimalField
from django.db.models.functions import Coalesce
from .models import Salary, SalaryType
from transactions.models import Transaction, Origin
from core.models import CalendarEvent
from core.selectors import get_cal_events_for_period
from typing import Any, Literal


def salary_calculate_total_by_employee_date(
    *,
    employees: QuerySet,
    cal_event: CalendarEvent,
    period: Literal["daily", "monthly"],
) -> list[dict[str, Any]]:

    if period == "daily":
        salary_date_q = Q(date=cal_event)
        transaction_date_q = Q(date=cal_event)
    else:
        cal_events = get_cal_events_for_period(cal_event=cal_event)
        salary_date_q = Q(date__in=cal_events)
        transaction_date_q = Q(date__in=cal_events)

    # --- Query 1: Salary aggregates per employee ---
    # Groups by employee, sums each salary type independently using conditional aggregation.
    # No JOIN to transactions here, so no cartesian product.
    salary_rows = (
        Salary.objects.filter(employee__in=employees)
        .filter(salary_date_q)
        .values("employee__employee_id")
        .annotate(
            salary_amount=Coalesce(
                Sum("amount", filter=Q(type=SalaryType.SALARY)),
                Decimal(0),
                output_field=DecimalField(),
            ),
            bonus_amount=Coalesce(
                Sum("amount", filter=Q(type=SalaryType.BONUS)),
                Decimal(0),
                output_field=DecimalField(),
            ),
            penalty_amount=Coalesce(
                Sum("amount", filter=Q(type=SalaryType.PENALTY)),
                Decimal(0),
                output_field=DecimalField(),
            ),
        )
    )
    salary_by_employee: dict[str, dict] = {
        row["employee__employee_id"]: row for row in salary_rows
    }

    # --- Query 2: Turnover — sum cart amounts, each sale counted once per employee ---
    # Groups by (employee, sale) to get one row per unique sale per employee,
    # then sums the cart amounts in Python to avoid any double-counting.
    sale_rows = (
        Salary.objects.filter(employee__in=employees, sale__isnull=False)
        .filter(salary_date_q)
        .values("employee__employee_id", "sale_id")
        .annotate(cart_amount=F("sale__cart__final_amount"))
    )
    turnover_by_employee: dict[str, Decimal] = {}
    seen_sales: set[tuple] = set()
    for row in sale_rows:
        key = (row["employee__employee_id"], row["sale_id"])
        if key not in seen_sales:
            seen_sales.add(key)
            emp_id = row["employee__employee_id"]
            turnover_by_employee[emp_id] = turnover_by_employee.get(
                emp_id, Decimal(0)
            ) + (row["cart_amount"] or Decimal(0))

    # --- Query 3: Transaction aggregates per employee ---
    # Groups by employee, sums paid salary and bonus independently.
    # No JOIN to salaries here, so no cartesian product.
    transaction_rows = (
        Transaction.objects.filter(employee__in=employees)
        .filter(transaction_date_q)
        .values("employee__employee_id")
        .annotate(
            paid_salary=Coalesce(
                Sum("amount", filter=Q(origin=Origin.SALARY)),
                Decimal(0),
                output_field=DecimalField(),
            ),
            paid_bonus=Coalesce(
                Sum("amount", filter=Q(origin=Origin.BONUS)),
                Decimal(0),
                output_field=DecimalField(),
            ),
        )
    )
    transaction_by_employee: dict[str, dict] = {
        row["employee__employee_id"]: row for row in transaction_rows
    }

    # --- Merge all data per employee ---
    # Iterates over the input employees queryset so every employee appears
    # in the result, even those with no salaries or transactions (all zeros).
    result = []
    for emp in employees.values("employee_id"):
        emp_id = emp["employee_id"]
        s = salary_by_employee.get(emp_id, {})
        t = transaction_by_employee.get(emp_id, {})

        salary_amount = s.get("salary_amount", Decimal(0))
        bonus_amount = s.get("bonus_amount", Decimal(0))
        penalty_amount = s.get("penalty_amount", Decimal(0))
        turnover_amount = turnover_by_employee.get(emp_id, Decimal(0))
        paid_salary = t.get("paid_salary", Decimal(0))
        paid_bonus = t.get("paid_bonus", Decimal(0))

        result.append(
            {
                "employee_id": emp_id,
                "salary_amount": salary_amount,
                "bonus_amount": bonus_amount,
                "penalty_amount": penalty_amount,
                "turnover_amount": turnover_amount,
                "paid_salary": paid_salary,
                "paid_bonus": paid_bonus,
                "balance": (
                    salary_amount
                    + bonus_amount
                    + penalty_amount
                    + paid_salary
                    + paid_bonus
                ),
            }
        )

    return result
