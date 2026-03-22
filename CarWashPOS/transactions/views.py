from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
class TransactionsOverview(LoginRequiredMixin, View):
    pass
