from .models import Sale, Cart
from core.models import CalendarEvent, Subscriber
from django.db.models import QuerySet
from decimal import Decimal


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
