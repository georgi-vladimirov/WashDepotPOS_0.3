from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import BaseModel
from decimal import Decimal

# from CashDesk.models import Transaction
from core.models import (
    Employee,
    Service,
    Subscriber,
    VehicleType,
    VehicleBrand,
    CalendarEvent,
)


class PaymentStatus(models.TextChoices):
    PAID = "PAID", _("Paid")
    UNPAID = "UNPAID", _("Unpaid")
    PARTIAL = "PARTIAL", _("Partial")


class Sale(BaseModel):
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    date = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="sales")
    vehicle_brand = models.ForeignKey(VehicleBrand, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    reg_number = models.CharField(max_length=15)
    manager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="manager_sales")
    worker = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="worker_sales")
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sales",
    )

    def __str__(self) -> str:
        return f"Sale on {self.date.date} at {self.date.location.name} | Reg#: {self.reg_number} | Active: {self.is_active}"

    # @property
    # def paid_amount(self) -> Decimal:
    #     """Calculate total amount paid from all transactions for this sale."""
    #     transactions = Transaction.objects.filter(sale=self)
    #     total_paid = transactions.aggregate(total_paid=models.Sum("amount"))["total_paid"] or Decimal(0)
    #     return total_paid


class Cart(BaseModel):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name="cart")
    services = models.ManyToManyField(Service, related_name="carts", blank=True)


# class CartItem(BaseModel):
#     name = models.CharField(max_length=200, default="")
#     service_type = models.CharField(max_length=50)
#     vehicle_type = models.CharField(max_length=20)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

#     def __str__(self) -> str:
#         return f"{self.name} - {self.service_type} ({self.vehicle_type}): {self.amount} | Active: {self.is_active}"
