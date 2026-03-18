from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger("accounts.selectors")


def get_authenticated_user(*, username: str, password: str) -> AbstractUser | None:
    user = authenticate(username=username, password=password)
    if user is not None:
        logger.info("user: %s authenticated.", user.username)
    else:
        logger.warning("Failed authentication attempt for username: %s", username)
    return user
