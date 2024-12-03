import django.conf
import django.contrib.auth.backends
import django.contrib.auth.models
import django.contrib.messages
import django.shortcuts
import django.urls
import django.utils.timezone

from lambda_search import users

__all__ = ()


class EmailOrUsernameModelBackend(django.contrib.auth.backends.BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if "@" in username:
                user = lambda_search.users.models.User.objects.by_mail(
                    username
                )

            else:
                user = lambda_search.users.models.User.objects.get(
                    username=username
                )

        except django.contrib.auth.models.User.DoesNotExist:
            return None

        if user:
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
                    (
                        "Вы превысили допустимое "
                        "число попыток входа. Пожалйста "
                        "активируйте свой аккаунт. "
                        "Вам должно прийти письмо на почту c активацией."
                    ),
                )

                activation_path = django.urls.reverse(
                    "users:activate",
                    args=[user.username],
                )
                confirmation_link = (
                    "Замечена подозрительная активность аккаунта. "
                    "Для того чтобы активировать свой аккаунт, "
                    "нажмите на ссылку ниже: "
                    f"http://127.0.0.1:8000{activation_path}"
                )

                django.core.mail.send_mail(
                    "Активация аккаунта",
                    confirmation_link,
                    django.conf.settings.MAIL,
                    [user.email],
                    fail_silently=False,
                )

        return None

    def get_user(self, user_id):
        try:
            return django.contrib.auth.models.User.objects.get(pk=user_id)
        except django.contrib.auth.models.User.DoesNotExist:
            return None
