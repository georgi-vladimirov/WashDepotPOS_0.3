from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
import http
from django.contrib.auth.mixins import LoginRequiredMixin
from .selectors import get_expences_by_cal_event
from core.selectors import get_cal_event_by_id
from .forms import AddExpenceForm


class ExpencesOverview(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.GET.get('cal_event_id')
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        print(cal_event_id)
        if not cal_event:
            return render(request, 'expences/overview.html', {'expences': []})

        expences = get_expences_by_cal_event(cal_event=cal_event)
        return render(request, 'expences/overview.html', {'expences': expences})


class AddExpence(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.GET.get('cal_event_id')
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if not cal_event:
            return HttpResponse("No calendar event selected", status=http.HTTPStatus.BAD_REQUEST)
        form = AddExpenceForm(date=cal_event)
        
        return render(request, 'expences/costs_entry.html', {'form': form})
            