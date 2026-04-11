from pathlib import Path
import os
import dj_database_url  # type: ignore[import-untyped]
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from common.logger import JSONFormatter

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# Application definition

INSTALLED_APPS = [
    "common",
    "core",
    "accounts",
    "sales",
    "transactions",
    "expences",
    "salaries",
    "reporting",
    "import_export",
    "rosetta",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "common.middleware.CurrentUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "CarWashPOS.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "CarWashPOS.wsgi.application"


# Database
DATABASES = {
    "default": dj_database_url.config(
        default=(
            f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
            f"@{os.environ.get('DB_HOST', '127.0.0.1')}:{os.environ.get('DB_PORT', '5432')}"
            f"/{os.environ.get('DB_NAME')}"
        ),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

LOCALE_PATHS = [BASE_DIR / "locale"]

USE_TZ = True

USE_THOUSAND_SEPARATOR = True


# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"


LANGUAGES = [
    ("en", _("English")),
    ("bg", _("Bulgarian")),
]

BETTER_STACK_TOKEN = os.environ.get("BETTER_STACK_TOKEN", None)

# Logging — file handler only when running locally (DEBUG=True)
# Render has an ephemeral filesystem so file logging is skipped in production.
_log_handlers = ["console", "betterstack"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JSONFormatter},
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "betterstack": {
            "()": "common.logger.BetterStackHandler",
            "token": BETTER_STACK_TOKEN,
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": _log_handlers,
            "level": "WARNING",
            "propagate": False,
        },
        "accounts": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "sales": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "transactions": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": False,
        },
    },
}

if DEBUG:
    LOGGING["handlers"]["file"] = {  # type: ignore[index]
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR / "logs/debug.jsonl",
        "formatter": "json",
        "maxBytes": 10_000_000,
        "backupCount": 5,
        "encoding": "utf-8",
    }
    for logger in LOGGING["loggers"].values():  # type: ignore[union-attr]
        logger["handlers"] = ["console", "file", "betterstack"]
