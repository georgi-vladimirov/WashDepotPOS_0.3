from core.models import CalendarEvent
from .models import Sale
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