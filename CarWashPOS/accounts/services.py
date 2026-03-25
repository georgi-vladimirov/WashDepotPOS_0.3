from django.contrib.auth import login, logout
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
import logging

logger = logging.getLogger("accounts.services")


def user_login(*, request: HttpRequest, user: AbstractUser) -> None:
    logger.info("user_logged_in", extra={"user_id": user.get_username()})
    
    login(request, user)


def user_logout(*, request: HttpRequest) -> None:
    logger.info("user_logged_out", extra={"user_id": request.user.get_username()})
    logout(request)
    