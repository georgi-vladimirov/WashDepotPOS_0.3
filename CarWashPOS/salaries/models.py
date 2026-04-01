from django.db import models
from common.models import BaseModel
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from core.models import CalendarEvent, Employee
from core.selectors import get_cal_events_for_month
from sales.models import Sale


class SalaryType(models.TextChoices):
    BONUS = "BONUS", _("Bonus")
    SALARY = "SALARY", _("Salary")
    PENALTY = "PENALTY", _("Penalty")   
    
    
class Salary(BaseModel):
    date = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="salaries")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salaries")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="salaries", blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    type = models.CharField(max_length=10, choices=SalaryType.choices, default=SalaryType.SALARY)

    class Meta(BaseModel.Meta):
        unique_together = ("date", "employee", "type", "sale")