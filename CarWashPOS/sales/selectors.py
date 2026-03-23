from .models import Sale, Cart, PaymentStatus
from core.models import CalendarEvent, Subscriber
from django.db.models import QuerySet
from decimal import Decimal
from transactions.selectors import get_trans_amount_by_sale


def get_sales_by_cal_event(*, cal_event: CalendarEvent) -> QuerySet[Sale]:
    """Return a QuerySet of Sale objects for the given CalendarEvent."""
    return Sale.objects.filter(date=cal_event).select_related(
        "vehicle_type", "vehicle_brand", "subscriber", "cart", "worker", "manager"
    )


def get_sale_by_id(*, sale_id: int) -> Sale | None:
    """Return a Sale by primary key, or None if not found."""
    return Sale.objects.filter(pk=sale_id).first()


def get_discount_for_subscriber_from_sale(*, sale: Sale) -> Decimal:
    """Return the discount percentage for a subscriber, or 0 if no subscriber."""
    subscriber: Subscriber | None = sale.subscriber
    if subscriber is None:
        return Decimal(0)
    return subscriber.discount_percentage


def get_cart_by_id(*, cart_id: int) -> Cart | None:
    """Return a Cart by primary key, or None if not found."""
    return Cart.objects.filter(pk=cart_id).first()


def get_sale_payment_status(*, sale: Sale) -> PaymentStatus:
    """Return the payment status of a sale."""
    return sale.payment_status


def get_cart_final_amount(*, cart: Cart) -> Decimal:
    """Return the final amount of a cart."""
    return cart.final_amount


def get_cart_by_sale(*, sale: Sale) -> Cart | None:
    """Return the Cart associated with a Sale, or None if not found."""
    return Cart.objects.filter(sale=sale).first()


def get_sale_unpaid_amount(*, sale: Sale) -> Decimal:
    """Return the paid amount of a sale."""
    cart: Cart | None = get_cart_by_sale(sale=sale)
    cart_amount: Decimal
    trans_amount: Decimal = get_trans_amount_by_sale(sale=sale)

    if cart is None:
        cart_amount = Decimal(0)
    else:
        cart_amount = get_cart_final_amount(cart=cart)

    return cart_amount - trans_amount