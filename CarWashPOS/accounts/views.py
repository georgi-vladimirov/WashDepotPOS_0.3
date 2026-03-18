from django.shortcuts import render, redirect
from django.views import View

from .selectors import get_authenticated_user
from .services import user_login, user_logout


class LoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "accounts/login.html")
        return redirect("core:home")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = get_authenticated_user(username=username, password=password)
        if user is not None:
            user_login(request=request, user=user)
            return redirect("core:home")
        return render(request, "accounts/login.html", {"error": "Invalid credentials"})


class LogoutView(View):
    def get(self, request):
        user_logout(request=request)
        return redirect("accounts:login")
