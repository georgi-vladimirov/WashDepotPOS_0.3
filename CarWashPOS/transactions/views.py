from logging import lastResort
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.selectors import get_cal_event_by_id
from sales.models import Sale
from sales.selectors import get_sale_by_id, get_sale_unpaid_amount
from .selectors import get_trans_by_cal_event, get_cash_end_from_prev_cal_event, get_tran_by_id
from .services import daily_report_calculate, transaction_save, transaction_operation_save, calculate_cash_balance, transaction_delete
from .forms import TransactionForm
from .models import Origin, TranType
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

        return render(request, "transactions/overview.html", {
            "transactions": transactions,
            "aggregates": aggregates,
            "fields":  ["type", "amount", "payment_method", "origin", "details"],
            "headers": ["Тип", "Сума", "Метод", "Произход", "Детайли"],
            "cal_event": cal_event
        })


class TranSales(LoginRequiredMixin, View):
    def get(self, request, sale_id: int|None = None, *args, **kwargs):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            return redirect("sales.sales_overview")

        form = self.get_form_for_sale(sale_id=sale_id)
        if form is None:
            return redirect("sales:sales_overview")
        form.date.initial = cal_event

        form_action = reverse('transactions:tran_sales', kwargs={"sale_id": sale_id})
        return render(request, "transactions/transaction.html", {"form": form, "form_action": form_action})

    def get_form_for_sale(self, sale_id: int | None) -> TransactionForm | None:
        if not sale_id:
            return None
        sale: Sale | None = get_sale_by_id(sale_id=sale_id)
        if sale is None:
            return None
        amount: Decimal = get_sale_unpaid_amount(sale=sale)
        return TransactionForm(amount=amount, sale=sale)

    def post(self, request, sale_id):
        print("hello")
        form: TransactionForm = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction_save(transaction=transaction)

        return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")


class Transactions(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")

        tran_type_str = request.GET.get("tran_type", "")
        tran_type = TranType(tran_type_str) if tran_type_str in TranType.values else None

        origin_str = request.GET.get("origin", "")
        origin = Origin(origin_str) if origin_str in Origin.values else None

        if not tran_type or not origin:
            return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")

        amount: Decimal = Decimal("0.00")
        if tran_type == TranType.START:
            last_end_trans = get_cash_end_from_prev_cal_event(cal_event=cal_event)
            amount: Decimal = last_end_trans.amount if last_end_trans else Decimal("0.00")
        if tran_type == TranType.END:
            amount: Decimal = calculate_cash_balance(cal_event=cal_event)

        form = TransactionForm(amount = amount, type=tran_type, origin=origin)
        form.date.initial = cal_event

        form_action = reverse('transactions:transactions')
        return render(request, "transactions/transaction.html", {"form": form, "form_action": form_action})

    def post(self, request):
        form: TransactionForm = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction_operation_save(transaction=transaction)

        return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")


class TranDelete(LoginRequiredMixin, View):
    def get(self, request, pk):
        transaction = get_tran_by_id(pk=pk)
        if transaction:
            transaction_delete(transaction=transaction)
        return redirect("transactions:trans_overview")
