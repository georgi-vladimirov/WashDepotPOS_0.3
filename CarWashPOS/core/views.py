from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import sync_cal_event_session, calendar_event_create
from .selectors import get_all_locations_by_user, get_location_by_id, get_cal_event_by_id, get_cal_events_for_month
import calendar
from datetime import date


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        sync_cal_event_session(request=request)
        return render(request, "core/home.html")


class CalendarView(LoginRequiredMixin, View):
    def get(self, request):
        locations = get_all_locations_by_user(user=request.user)

        today = date.today()
        selected_month = int(request.GET.get("month", today.month))
        selected_year = int(request.GET.get("year", today.year))
        selected_location_id = request.GET.get("location")

        selected_location = (
            get_location_by_id(location_id=selected_location_id) if selected_location_id else locations.first()
        )

        events = (
            get_cal_events_for_month(location=selected_location, year=selected_year, month=selected_month)
            if selected_location
            else {}
        )

        context = {
            "calendar": calendar.monthcalendar(selected_year, selected_month),
            "month_name": calendar.month_name[selected_month],
            "selected_month": selected_month,
            "selected_year": selected_year,
            "selected_location": selected_location,
            "locations": locations,
            "events": events,
            "months": [(i, calendar.month_name[i]) for i in range(1, 13)],
            "years": list(range(today.year - 2, today.year + 2)),
            "today": today,
        }

        return render(request, "core/calendar.html", context)


class SetDateLocationView(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.GET.get("eventId")

        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if cal_event:
            request.session["cal_event_id"] = cal_event.pk
        return redirect("core:home")


class CreateNewCalendarEventView(LoginRequiredMixin, View):
    def get(self, request):
        date_str = request.GET.get("date")
        location_id = request.GET.get("location")

        cal_event = calendar_event_create(date_str, location_id)
        request.session["cal_event_id"] = cal_event.pk
        return redirect("core:home")
