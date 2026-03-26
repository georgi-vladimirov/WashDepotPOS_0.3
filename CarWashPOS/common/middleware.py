import threading
from django.http import HttpRequest, HttpResponse

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, "user", None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        _thread_locals.user = user if user and user.is_authenticated else None
        response = self.get_response(request)
        _thread_locals.user = None  # изчиства след заявката
        return response
