from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.selectors import get_cal_event_by_id
from sales.models import Sale
from sales.selectors import get_sale_by_id, get_sale_unpaid_amount
from .selectors import get_trans_by_cal_event
from .services import daily_report_calculate, transaction_save
from .forms import TransactionForm
from .models import PaymentMethod, Transaction
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


class TranSales(LoginRequiredMixin, View):
    def get(self, request, sale_id: int|None = None, *args, **kwargs):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            return redirect("sales.sales_overview")

        sale: Sale | None = None
        if sale_id:
            sale = get_sale_by_id(sale_id=sale_id)
        if sale is None:
            messages.error(request, "Sale not found")
            return redirect("sales:sales_overview")
        amount: Decimal = get_sale_unpaid_amount(sale=sale)
        form: TransactionForm = TransactionForm(amount = amount, sale=sale)
        form.date.initial = cal_event

        return render(request, "transactions/transaction.html", {"form": form, "title": "Payment", "sale": sale})

    def post(self, request):
        # cal_event_id = request.session.get("cal_event_id")
        # cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        # if cal_event is None:
        #     return redirect("sales.sales_overview")

        form: TransactionForm = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction_save(transaction=transaction)

        return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")
