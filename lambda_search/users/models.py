import argparse
import re

import django.conf
import django.contrib.auth.models
from django.core.validators import FileExtensionValidator
import django.db
from django.utils.translation import gettext_lazy as _
import sorl.thumbnail

__all__ = ()


def should_modify_email_field():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="")
    args, _ = parser.parse_known_args()
    return args.command not in ["makemigrations", "migrate"]


if should_modify_email_field():
    model = django.contrib.auth.models.User
    model._meta.get_field("email")._unique = True


class UserManager(django.contrib.auth.models.UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related("profile")

    def normalize_email(self, email):
        email = super().normalize_email(email)
        email = email.lower()
        local_part, domain = email.split("@")

        local_part = local_part.split("+")[0]

        if domain in ["yandex.ru", "ya.ru"]:
            domain = "yandex.ru"
            local_part = local_part.replace(".", "-")
        elif domain == "gmail.com":
            local_part = local_part.replace(".", "")

        local_part = re.sub(r"\+.*", "", local_part)
        return f"{local_part}@{domain}"

    def active(self):
        return (
            self.get_queryset()
            .filter(is_active=True)
            .select_related("profile")
        )

    def by_mail(self, identifier):
        normalized_email = self.normalize_email(identifier)
        return self.active().get(email=normalized_email)


class User(django.contrib.auth.models.User):
    objects = UserManager()

    def create_profile(self):
        if not hasattr(self, "profile"):
            Profile.objects.create(user=self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_profile()

    class Meta:
        proxy = True
        db_table = "auth_user"


def file_size(value):
    limit = 50 * 1024 * 1024
    if value.size > limit:
        raise django.core.exceptions.ValidationError(
            _("Файл слишком большой, максимум 50 МБ"),
        )


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.conf.settings.AUTH_USER_MODEL,
        on_delete=django.db.models.CASCADE,
        related_name="profile",
        verbose_name=_("профиль"),
    )
    image = django.db.models.ImageField(
        "путь к изображению профиля",
        upload_to="users/images/",
        help_text=_("Upload a profile picture"),
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(["png", "jpeg", "jpg"]),
            file_size,
        ],
    )

    attempts_count = django.db.models.PositiveIntegerField(
        default=0,
    )
    date_last_active = django.db.models.DateTimeField(null=True, blank=True)

    def get_small_avatar(self):
        if self.image:
            return sorl.thumbnail.get_thumbnail(
                self.image,
                "32x32",
                crop="center",
            ).url

        return None

    def get_big_avatar(self):
        if self.image:
            return sorl.thumbnail.get_thumbnail(
                self.image,
                "120x120",
                crop="center",
            ).url

        return None

    class Meta:
        verbose_name = _("профиль")
        verbose_name_plural = _("профили")
