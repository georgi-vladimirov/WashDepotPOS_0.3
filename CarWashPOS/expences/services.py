from typing import Tuple
from django.utils.translation import gettext_lazy as _
from .models import Expence
from cal_app.models import CalendarEvent
from django.db.models import QuerySet
from transactions.models import Transaction, TranType, Origin, PaymentMethod
from transactions.services import create_tran_for_expence, transaction_delete
import logging

logger = logging.getLogger("expences.services")


def save_expence(*, expence: Expence) -> Tuple[bool, str]:
    transaction = create_tran_for_expence(
        date=expence.date, amount=-expence.amount, details=expence.name
    )
    transaction.save()
    expence.transaction = transaction
    expence.save()
    logger.info("expence_saved", extra={"expence": expence.logger_data()})
    return True, str(_("Expence saved successfully"))


def delete_expence(*, expence: Expence) -> Tuple[bool, str]:
    result = transaction_delete(
        transaction=expence.transaction
    )  # When transaction is deleted, expence is also deleted due to CASCADE
    if result:
        logger.info("expence_deleted", extra={"expence": expence.logger_data()})
        message = str(_("Expence deleted successfully"))
    else:
        logger.warning("expence_not_deleted", extra={"expence": expence.logger_data()})
        message = str(_("Expence not deleted"))
    return result, message
