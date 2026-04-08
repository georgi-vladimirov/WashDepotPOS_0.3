import calendar
from datetime import date

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from core.selectors import get_cal_event_by_id
from .services import get_data_for_monthly_report, monthly_report_pivot


class MonthlyReport(View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if not cal_event:
            return HttpResponse("Cal event not found", status=404)

        # Read year/month from GET params, fall back to the cal_event's date
        selected_year = int(request.GET.get("year", cal_event.date.year))
        selected_month = int(request.GET.get("month", cal_event.date.month))

        (
            sales_data,
            transactions_data,
            cartItems_data,
            costs_data,
            salaries_data,
            bonus_data,
        ) = get_data_for_monthly_report(
            cal_event=cal_event,
            year=selected_year,
            month=selected_month,
        )

        rows, columns = monthly_report_pivot(
            year=selected_year,
            month=selected_month,
            location=cal_event.location,
            sales_data=sales_data,
            transactions_data=transactions_data,
            cartItems_data=cartItems_data,
            costs_data=costs_data,
            salaries_data=salaries_data,
            bonus_data=bonus_data,
        )

        current_year = date.today().year
        years = list(range(current_year - 3, current_year + 2))
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]

        context = {
            "rows": rows,
            "columns": columns,
            "cal_event": cal_event,
            "selected_year": selected_year,
            "selected_month": selected_month,
            "years": years,
            "months": months,
        }

        return render(request, "reporting/overview.html", context)
