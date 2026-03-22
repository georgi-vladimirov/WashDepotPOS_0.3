from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from core.selectors import get_cal_event_by_id
from .selectors import get_trans_by_cal_event
from .services import daily_report_calculate
from .filters import FILTERS

# Create your views here.
class TransactionsOverview(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)

        if cal_event is None:
            return render(request, "transactions/overview.html")

        transactions = get_trans_by_cal_event(cal_event=cal_event)
        aggregates = daily_report_calculate(transactions_qs=transactions, filters=FILTERS)

        return render(request, "transactions/overview.html", {"transactions": transactions, "aggregates": aggregates})
