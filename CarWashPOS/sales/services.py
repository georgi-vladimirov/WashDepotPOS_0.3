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
