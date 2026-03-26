from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import BaseModel
from decimal import Decimal

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
    vehicle_brand = models.ForeignKey(VehicleBrand, on_delete=models.PROTECT)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    reg_number = models.CharField(max_length=15)
    manager = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="manager_sales")
    worker = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="worker_sales")
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales",
    )
    ################
    display_fields: list[str] = ["vehicle_brand", "vehicle_type", "reg_number"]
    ################
    def __str__(self) -> str:
        return f"{self.date.date} - {self.date.location.name} - {self.reg_number} - {self.vehicle_brand.brand}"

    @property
    def paid_amount(self) -> Decimal:
        """Calculate total amount paid from all transactions for this sale."""
        from transactions.selectors import get_trans_amount_by_sale
        total_paid = get_trans_amount_by_sale(sale = self)
        return total_paid


class Cart(BaseModel):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name="cart")
    services = models.ManyToManyField(
        "core.Service",
        through="CartItem",
        related_name="carts",
        blank=True,
    )
    ################
    display_fields: list[str] = ["final_amount"]
    ################

    def __str__(self) -> str:
        return f"{self.sale.id} - {self.total_amount} - {self.discount} - {self.final_amount}"



class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_price = models.ForeignKey(
        "core.ServicePrice",
        on_delete=models.PROTECT,  # prevent deleting a price that was charged
        related_name="cart_items",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of sale
    ################
    display_fields: list[str] = ["service", "service_price"]
    ################
    class Meta(BaseModel.Meta):
        unique_together = ("cart", "service")
