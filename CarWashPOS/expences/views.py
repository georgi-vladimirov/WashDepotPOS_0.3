import http
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from core.selectors import get_cal_event_by_id
from .selectors import get_expences_by_cal_event, get_expence_by_id
from .services import save_expence, delete_expence
from .forms import AddExpenceForm


class ExpencesOverview(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if not cal_event:
            return render(request, 'expences/overview.html', {'expences': []})
        expences = get_expences_by_cal_event(cal_event=cal_event)
        return render(request, 'expences/overview.html', {'expences': expences})


class AddExpence(LoginRequiredMixin, View):
    def get(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if not cal_event:
            return HttpResponse("No calendar event selected", status=http.HTTPStatus.BAD_REQUEST)
        form = AddExpenceForm(date=cal_event)

        return render(request, 'expences/costs_entry.html', {'form': form})

    def post(self, request):
        cal_event_id = request.session.get("cal_event_id")
        cal_event = get_cal_event_by_id(cal_event_id=cal_event_id)
        if not cal_event:
            return HttpResponse("No calendar event selected", status=http.HTTPStatus.BAD_REQUEST)
        form = AddExpenceForm(request.POST, date=cal_event)
        if form.is_valid():
            expence = form.save(commit=False)
            save_expence(expence=expence)
            return HttpResponse("<script>window.opener.location.reload(); window.close();</script>")
        return render(request, 'expences/costs_entry.html', {'form': form})


class DeleteExpence(LoginRequiredMixin, View):
    def get(self, request, pk):
        expence = get_expence_by_id(pk=pk)
        if not expence:
            return HttpResponse("Expence not found", status=http.HTTPStatus.NOT_FOUND)
        result, message = delete_expence(expence=expence)
        if result:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('expences:overview')
