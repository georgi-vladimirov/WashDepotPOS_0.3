from django.contrib.auth import login, logout
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
import logging

logger = logging.getLogger("accounts.services")


def user_login(*, request: HttpRequest, user: AbstractUser) -> None:
    logger.info("user: %s logged in.", user.username)
    login(request, user)


def user_logout(*, request: HttpRequest) -> None:
    logger.info("user: %s logged out.", request.user.username)
    logout(request)
