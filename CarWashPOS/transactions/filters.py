from .models import TranType, Origin, PaymentMethod
from django.utils.translation import gettext_lazy as _


FILTERS = {
    # Define filter criteria for each aggregate. Each entry contains
    # a `filter_kwargs` dict to pass to QuerySet.filter() and an
    # `order` value used by the caller/UI.
    "START": {
        "filter_kwargs": {"type": TranType.START},
        "order": 1,
        "label": _("Cash at Start"),
    },
    "DEPOSIT": {
        "filter_kwargs": {
            "type": TranType.IN,
            "origin": Origin.DEPOSIT,
        },
        "order": 2,
        "label": _("Deposit"),
    },
    "INCOME_CASH": {
        "filter_kwargs": {
            "type": TranType.IN,
            "origin": Origin.INCOME,
            "payment_method": PaymentMethod.CASH,
        },
        "order": 3,
        "label": _("Income Cash"),
    },
    "WITHDRAW": {
        "filter_kwargs": {
            "type": TranType.OUT,
            "origin": Origin.WITHDRAW,
            "payment_method": PaymentMethod.CASH,
        },
        "order": 4,
        "label": _("Withdrawals"),
    },
    "COSTS": {
        "filter_kwargs": {
            "type": TranType.OUT,
            "origin": Origin.COST,
            "payment_method": PaymentMethod.CASH,
        },
        "order": 5,
        "label": _("Costs"),
    },
    "SALARIES": {
        "filter_kwargs": {
            "type": TranType.OUT,
            "origin": Origin.SALARY,
            "payment_method": PaymentMethod.CASH,
        },
        "order": 6,
        "label": _("Salaries"),
    },
    "BONUS": {
        "filter_kwargs": {
            "type": TranType.OUT,
            "origin": Origin.BONUS,
            "payment_method": PaymentMethod.CASH,
        },
        "order": 7,
        "label": _("Bonus"),
    },
    "END": {
        "filter_kwargs": {"type": TranType.END},
        "order": 8,
        "label": _("Cash at End"),
    },
    "INCOME_CARD": {
        "filter_kwargs": {
            "type": TranType.IN,
            "origin": Origin.INCOME,
            "payment_method": PaymentMethod.POS,
        },
        "order": 11,
        "label": _("Income Card"),
    },
    "POS_RECEIPT": {
        "filter_kwargs": {"type": TranType.POS},
        "order": 12,
        "label": _("POS Receipt"),
    },
}
