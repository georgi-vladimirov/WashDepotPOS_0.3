from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.selectors import get_cal_event_by_id, get_employees_for_location
from transactions.models import Origin
from transactions.services import transaction_salary_save
from transactions.forms import TransactionForm
from .selectors import (
    salary_calculate_total_by_employee_date,
    get_penalties_by_cal_event,
    get_penalties_by_month,
    get_salary_by_pk
)
from .services import create_penalty, delete_penalty
from decimal import Decimal
from django.contrib import messages


class SalariesOverview(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)

        if cal_event is None:
            return render(request, "salaries/salaries_overview.html")

        employees = get_employees_for_location(location=cal_event.location)
        salary_aggregates_daily = salary_calculate_total_by_employee_date(
            employees=employees, cal_event=cal_event, period="daily"
        )
        salary_aggregates_monthly = salary_calculate_total_by_employee_date(
            employees=employees, cal_event=cal_event, period="monthly"
        )
        penalties_daily = get_penalties_by_cal_event(cal_event=cal_event)
        penalties_monthly = get_penalties_by_month(cal_event=cal_event)

        return render(
            request,
            "salaries/salaries_overview.html",
            {
                "salary_aggregates_daily": salary_aggregates_daily,
                "salary_aggregates_monthly": salary_aggregates_monthly,
                "penalties_daily": penalties_daily,
                "penalties_monthly": penalties_monthly,
            },
        )


class PaymentView(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)

        if cal_event is None:
            return render(request, "salaries/salaries_overview.html")

        origin_str = request.GET.get("origin", "")
        origin = Origin(origin_str) if origin_str in Origin.values else None

        form = TransactionForm(
            origin=origin, is_employee=True, location=cal_event.location
        )
        form.date.initial = cal_event
        form_action = reverse("salaries:payment")

        return render(
            request,
            "transactions/transaction.html",
            {
                "form": form,
                "form_action": form_action,
                "title": origin.label,  # type: ignore
            },
        )

    def post(self, request):
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction_salary_save(transaction=transaction)
        return HttpResponse(
            "<script>window.opener.location.reload(); window.close();</script>"
        )


class PenaltyView(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            return render(request, "salaries/salaries_overview.html")

        employees = get_employees_for_location(location=cal_event.location)
        return render(request, "salaries/penalty.html", {"employees": employees})

    def post(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event is None:
            return HttpResponse(
                "<script>window.opener.location.reload(); window.close();</script>"
            )

        employee_id = request.POST.get("employee_id")
        amount: Decimal = Decimal(request.POST.get("amount"))
        create_penalty(cal_event=cal_event, employee_id=employee_id, amount=amount)

        return HttpResponse(
            "<script>window.opener.location.reload(); window.close();</script>"
        )


class SalaryDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        penalty = get_salary_by_pk(pk=pk)
        if penalty is None:
            return redirect("salaries:salaries_overview")

        result = delete_penalty(penalty)
        if result:
            messages.success(request, "Penalty deleted successfully.")
        else:
            messages.error(request, "Failed to delete penalty.")
        return redirect("salaries:salaries_overview")

