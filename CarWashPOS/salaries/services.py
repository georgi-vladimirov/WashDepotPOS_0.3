from .models import Salary, SalaryType
from sales.models import Sale
from core.models import Employee
from decimal import Decimal
from core.selectors import get_employee_by_id
from core.models import CalendarEvent


def create_salary(sale: Sale) -> list[Salary]:
    """Create and save salary/bonus records for worker and manager using bulk insert."""
    salaries_to_create: list[Salary] = []
    employees: list[Employee] = [sale.worker, sale.manager]
    sale_amount: Decimal = sale.cart.final_amount  # type: ignore

    for employee in employees:
        if employee.salary_percentage > 0:
            amount: Decimal = round(
                (employee.salary_percentage / Decimal(100)) * sale_amount, 2
            )
            salaries_to_create.append(
                Salary(
                    date=sale.date,
                    employee=employee,
                    sale=sale,
                    amount=amount,
                    type=SalaryType.SALARY,
                )
            )

        if employee.bonus_percentage > 0:
            amount: Decimal = round(
                (employee.bonus_percentage / Decimal(100)) * sale_amount, 2
            )
            salaries_to_create.append(
                Salary(
                    date=sale.date,
                    employee=employee,
                    sale=sale,
                    amount=amount,
                    type=SalaryType.BONUS,
                )
            )
    for salary in salaries_to_create:
        salary.full_clean()

    return Salary.objects.bulk_create(salaries_to_create)


def create_penalty(
    cal_event: CalendarEvent, employee_id: str, amount: Decimal
) -> Salary:
    employee = get_employee_by_id(employee_id=employee_id)
    if amount > 0:
        amount = -amount
    penalty = Salary(
        date=cal_event,
        employee=employee,
        amount=amount,
        type=SalaryType.PENALTY,
    )
    penalty.full_clean()
    penalty.save()
    return penalty


def delete_penalty(penalty: Salary) -> bool:
    result = penalty.delete()
    if result[0] > 0:
        return True
    return False
