import logging

import django.conf
import django.contrib.auth.backends
import django.contrib.auth.models
import django.contrib.messages
import django.shortcuts
import django.urls
import django.utils.timezone
from django.utils.translation import gettext_lazy as _

import search.encryptor
import users.models

__all__ = ()
logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(django.contrib.auth.backends.BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if "@" in username:
                user = users.models.User.objects.by_mail(username)

            else:
                user = users.models.User.objects.get(username=username)

        except django.contrib.auth.models.User.DoesNotExist:
            return None

        if user:
            try:
                user.profile
            except Exception:
                users.models.Profile.objects.create(user=user)

            if user.check_password(password):
                user.profile.attempts_count = 0
                return user

            if (
                user.profile.attempts_count
                < django.conf.settings.MAX_AUTH_ATTEMPTS - 1
            ):
                user.profile.attempts_count += 1
                user.profile.save()

            else:
                user.is_active = False
                user.profile.date_last_active = django.utils.timezone.now()
                user.save()
                user.profile.save()

                django.contrib.messages.error(
                    request,
                    _(
                        "You have exceeded the limit"
                        "number of login attempts. Please "
                        "activate your account."
                        "You should receive an activation email.",
                    ),
                )

                cell = search.encryptor.CellEncryptor(
                    django.conf.settings.ENCRYPTION_KEY,
                )

                activation_path = django.urls.reverse(
                    "users:activate",
                    args=[
                        cell.encrypt(username),
                    ],
                )
                confirmation_link = _(
                    "Suspicious account activity has been detected."
                    " To activate your account, click on the link below:"
                    f"{django.conf.settings.SITE_URL}{activation_path}",
                )
                try:

                    django.core.mail.send_mail(
                        "Account activation",
                        confirmation_link,
                        django.conf.settings.MAIL,
                        [
                            users.models.UserManager().normalize_email(
                                user.email,
                            ),
                        ],
                        fail_silently=False,
                    )
                except Exception as ex:
                    logger.debug(ex)

        return None

    def get_user(self, user_id):
        try:
            return django.contrib.auth.models.User.objects.get(pk=user_id)
        except django.contrib.auth.models.User.DoesNotExist:
            return None
