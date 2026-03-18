from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.views import View


# Create your views here.
class LoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "accounts/login.html")
        else:
            return redirect("core:home")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("core:home")
        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:login")
