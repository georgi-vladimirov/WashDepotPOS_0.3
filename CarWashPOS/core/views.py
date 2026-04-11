from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import sync_cal_event_session


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        sync_cal_event_session(request=request)
        return render(request, "core/home.html")
