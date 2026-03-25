from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel
from core.models import CalendarEvent, Employee
from sales.models import Sale


class TranType(models.TextChoices):
    IN = "IN", "In"
    OUT = "OUT", "Out"
    START = "START", "Start"
    END = "END", "End"
    POS = "POS", "POS Statement"


class Origin(models.TextChoices):
    INCOME = "INCOME", _("Income")
    COST = "COST", _("Cost")
    SALARY = "SALARY", _("Salary")
    BONUS = "BONUS", _("Bonus")
    DEPOSIT = "DEPOSIT", _("Deposit")
    WITHDRAW = "WITHDRAW", _("Withdrawal")
    BALANCE = "BALANCE", _("Balance")

class PaymentMethod(models.TextChoices):
    CASH = "CASH", _("Cash")
    POS = "POS", _("POS")
    ONLINE = "ONLINE", _("Online")
    SUBSCRIPTION = "SUBSCRIPTION", _("Subscription")
    PREPAID = "PREPAID", _("Prepaid")
    BANK = "BANK", _("Bank")

class Transaction(BaseModel):
    date = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=15, choices=TranType.choices)
    origin = models.CharField(max_length=15, choices=Origin.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices)
    ################################
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    ################################
    details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Convert amount to negative if transaction type is OUT
        if self.type == TranType.OUT and self.amount > 0:
            self.amount = -self.amount
        else:
            self.amount = abs(self.amount)
        super().save(*args, **kwargs)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["date", "type"],
                condition=models.Q(type__in=["POS", "START", "END"]),
                name="unique_pos_start_end_per_date",
            )
        ]
