from decimal import Decimal

from core.models import CalendarEvent
from core.selectors import get_services_by_location_and_vehicle_type, get_services_by_ids
from core.models import ServiceType, Service
from .models import Sale, Cart
import logging

logger = logging.getLogger("sales.services")


def create_sale(*, form, cal_event: CalendarEvent) -> Sale:
    sale = form.save(commit=False)
    sale.date = cal_event
    sale.save()
    logger.info("New sale recorded: %s", sale)
    return sale


def delete_sale(*, sale_id: int) -> bool:
    try:
        sale = Sale.objects.get(pk=sale_id)
        sale.delete()
        logger.info("Sale deleted: %s", sale)
        return True
    except Sale.DoesNotExist:
        logger.warning("Attempt to delete non-existent sale with id: %d", sale_id)
        return False


def create_cart_for_sale(
    *, sale: Sale, service_ids: list[str], total_amount: Decimal, discount_per: Decimal, final_amount: Decimal
) -> Cart:
    services = get_services_by_ids(service_ids=service_ids)
    cart = Cart.objects.create(
        sale=sale,
        total_amount=total_amount,
        discount=final_amount - total_amount,
        final_amount=final_amount,
    )
    cart.services.set(services)
    if not check_cart_amounts(cart=cart, discount_per=discount_per):
        logger.error("Cart amounts do not match expected values for sale %d", sale.pk)
        return cart  # Cart is still created, but amounts are inconsistent
    cart.save()
    logger.info("Cart created for sale %d with services: %s", sale.pk, service_ids)
    return cart


def check_cart_amounts(*, cart: Cart, discount_per: Decimal) -> bool:
    """Check if the cart's total_amount, discount, and final_amount are consistent with the services in the cart."""
    calculated_total = sum(
        s.service_prices.filter(vehicle_type=cart.sale.vehicle_type, location=cart.sale.date.location).first().amount
        for s in cart.services.all()
    )
    discount_amount = ((calculated_total * discount_per) / Decimal(100)) * -1
    expected_final = calculated_total + discount_amount

    total_match = calculated_total == cart.total_amount
    discount_match = discount_amount == cart.discount
    final_match = expected_final == cart.final_amount

    if total_match and discount_match and final_match:
        return True
    return False


def select_services_for_sale(*, sale: Sale):

    services = get_services_by_location_and_vehicle_type(location=sale.date.location, vehicle_type=sale.vehicle_type)
    service_types = ServiceType.objects.filter(services__in=services).distinct().order_by("order")

    services_by_type = []

    for st in service_types:
        st_services = services.filter(service_type=st)
        services_by_type.append(
            {
                "service_type_name": st.name,
                "service_type_name_BG": st.name_BG,
                "services": [
                    {
                        "id": s.id,  # type: ignore
                        "name": s.name,
                        "price": float(
                            s.service_prices.filter(  # type: ignore
                                vehicle_type=sale.vehicle_type,
                                location=sale.date.location,
                                is_active=True,
                            )
                            .first()
                            .amount
                        ),
                    }
                    for s in st_services
                ],
            }
        )

    return services_by_type
