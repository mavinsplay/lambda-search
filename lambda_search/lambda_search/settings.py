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
    "4f7Z7JU2q8dXOiAgR2fW1niOZTLGUexLGo3E4LL0oSi8mg1p",
)

ENCRYPTION_KEY = os.getenv(
    "DJANGO_ENCRYPTION_KEY",
    "dsEa3e6lF983WPH88NsSS9A0HGCIK5xA",
).encode()

DEBUG = env_validator(os.getenv("DJANGO_DEBUG", "true"))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "lamdba-search.ru").split(
    ",",
)

CSRF_TRUSTED_ORIGINS = [f"https://{x}" for x in ALLOWED_HOSTS]

DEFAULT_USER_IS_ACTIVE = env_validator(
    os.getenv("DJANGO_DEFAULT_USER_IS_ACTIVE", "true" if DEBUG else "false"),
)

MAIL = "lambda-search@yandex.ru"

EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "smtp.yandex.ru")
EMAIL_HOST_PASSWORD = os.getenv(
    "DJANGO_EMAIL_HOST_PASSWORD",
    "fxzxpenjgrrxjrtk",
)


BASE_DIR = Path(__file__).resolve().parent.parent

SITE_URL = os.getenv("DJANGO_SITE_URL", "http://127.0.0.1:8000")

INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cleanup.apps.CleanupConfig",
    # Local apps
    "about.apps.AboutConfig",
    "feedback.apps.FeedbackConfig",
    "history.apps.HistoryConfig",
    "homepage.apps.HomepageConfig",
    "search.apps.SearchConfig",
    "users.apps.UsersConfig",
    # Third-party apps
    "sorl.thumbnail",
    "turnstile",
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


DB_NAME = os.getenv("DJANGO_POSTGRESQL_NAME", "lambda_search")
DB_USER = os.getenv("DJANGO_POSTGRESQL_USER", "postgres")
DB_PASSWORD = os.getenv("DJANGO_POSTGRESQL_PASSWORD", "root")
DB_HOST = os.getenv("DJANGO_POSTGRESQL_HOST", "localhost")
DB_PORT = int(os.getenv("DJANGO_POSTGRESQL_PORT", "5432"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    },
}
LAMBDA_DBS_DIR = BASE_DIR / "lambda-dbs"

AUTH_PWD_MODULE = "django.contrib.auth.password_validation."

MAX_AUTH_ATTEMPTS = int(os.getenv("DJANGO_MAX_AUTH_ATTEMPTS", "5"))

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailOrUsernameModelBackend",
]

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

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = MAIL
EMAIL_USE_TLS = True
EMAIL_HOST_USER = MAIL
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CAPTCHA_ENABLED = env_validator(
    os.getenv("DJANGO_ALLOW_CAPTCHA", str(not DEBUG)),
)
if CAPTCHA_ENABLED:
    TURNSTILE_SITEKEY = os.getenv("DJANGO_CAPTCHA_SITE_KEY")
    TURNSTILE_SECRET = os.getenv("DJANGO_CAPTCHA_SECRET_KEY")

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INSTALLED_APPS.insert(0, "debug_toolbar")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]
