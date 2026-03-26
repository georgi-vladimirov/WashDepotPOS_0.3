from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger("accounts.selectors")


def get_authenticated_user(*, username: str, password: str) -> AbstractUser | None:
    user = authenticate(username=username, password=password)
    if user is not None:
        logger.info("user_authenticated", extra={"user_id": user.get_username()})
    else:
        logger.info("user_authentication_failed", extra={"username": username})

    return user # type: ignore
    