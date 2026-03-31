import http
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class SalariesOverview(LoginRequiredMixin, View):
    template_name = "salaries/salaries_overview.html"
