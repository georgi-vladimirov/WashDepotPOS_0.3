from django.db import models
from common.models import BaseModel
from cal_app.models import CalendarEvent
from transactions.models import Transaction


class Expence(BaseModel):
    date = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="expences"
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    details = models.TextField(blank=True, null=True)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="expences"
    )

    display_fields: list[str] = ["name", "amount"]
