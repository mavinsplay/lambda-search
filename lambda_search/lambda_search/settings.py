import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

__all__ = ()

load_dotenv()


def env_validator(env: str):
    return env.lower() in ["true", "yes", "1", "y", "t"]


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-g^_9#0r_apxp3u27(sbh$-67hmm6mu1u5x0%eto309@091)!b-",
)

DEBUG = env_validator(os.getenv("DJANGO_DEBUG", "true"))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

DEFAULT_USER_IS_ACTIVE = env_validator(
    os.getenv("DJANGO_DEFAULT_USER_IS_ACTIVE", "true" if DEBUG else "false"),
)

MAIL = os.getenv("DJANGO_MAIL", "django_mail@example.com")

BASE_DIR = Path(__file__).resolve().parent.parent


INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "homepage.apps.HomepageConfig",
    "search.apps.SearchConfig",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.ProxyUserMiddleware",
]

ROOT_URLCONF = "lambda_search.urls"

template_dirs = [BASE_DIR / "templates"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": template_dirs,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lambda_search.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

LAMBDA_DBS_DIR = BASE_DIR / "lambda-dbs"

if LAMBDA_DBS_DIR.exists():
    for db_file in LAMBDA_DBS_DIR.glob("*.sqlite3"):
        db_name = db_file.stem
        DATABASES[db_name] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_file,
        }

ATABASE_ROUTERS = ["path.to.database_router.DatabaseRouter"]

AUTH_PWD_MODULE = "django.contrib.auth.password_validation."

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": f"{AUTH_PWD_MODULE}UserAttributeSimilarityValidator",
    },
    {
        "NAME": f"{AUTH_PWD_MODULE}MinimumLengthValidator",
    },
    {
        "NAME": f"{AUTH_PWD_MODULE}CommonPasswordValidator",
    },
    {
        "NAME": f"{AUTH_PWD_MODULE}NumericPasswordValidator",
    },
]

TIME_ZONE = "UTC"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = LOGIN_URL

USE_TZ = True

STATIC_ROOT = BASE_DIR / "static"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

LANGUAGE_CODE = "ru"

LANGUAGES = [
    ("en-US", _("English")),
    ("ru-RU", _("Russian")),
]

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (BASE_DIR / "locale",)

ITEMS_PER_PAGE = 5

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"

EMAIL_FILE_PATH = BASE_DIR / "send_mail"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INSTALLED_APPS.insert(0, "debug_toolbar")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]
