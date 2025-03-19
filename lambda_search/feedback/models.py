from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ()


class Feedback(models.Model):
    STATUS_CHOICES = [
        ("received", "получено"),
        ("processing", "в обработке"),
        ("answered", "ответ дан"),
    ]

    text = models.CharField("Текст", max_length=100)
    created_on = models.DateTimeField(
        _("Создано в"),
        auto_now_add=True,
        null=True,
    )
    status = models.CharField(
        _("Статус обработки"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="received",
    )
    author = models.OneToOneField(
        "UserInfo",
        on_delete=models.CASCADE,
        related_name="feedback",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Обратная связь")
        verbose_name_plural = _("Обратные связи")


class UserInfo(models.Model):
    name = models.CharField(_("Имя"), max_length=100, null=True, blank=True)
    mail = models.EmailField(_("Почта"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    user_info = models.OneToOneField(
        Feedback,
        on_delete=models.CASCADE,
        related_name="userinfo",
        null=True,
        blank=True,
        verbose_name=_("Информация о пользователе"),
    )

    class Meta:
        verbose_name = _("Информация о пользователе")
        verbose_name_plural = _("Информация о пользователях")

    def __str__(self):
        return self.name or _("Аноним")


class StatusLog(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name=_("Обратная связь"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    timestamp = models.DateTimeField(_("Создано в"), auto_now_add=True)
    from_status = models.CharField(
        _("Из"),
        max_length=20,
        choices=Feedback.STATUS_CHOICES,
        db_column="from",
    )
    to = models.CharField(
        _("В"),
        max_length=20,
        choices=Feedback.STATUS_CHOICES,
        db_column="to",
    )

    class Meta:
        verbose_name = _("Лог изменения статуса")
        verbose_name_plural = _("Логи изменения статусов")

    def __str__(self):
        return _(
            (
                f"Статус изменен с {self.from_status} н"
                f"а {self.to} пользователем {self.user}"
            ),
        )


class FeedbackFile(models.Model):
    def upload_to_path(self, filename):
        return f"uploads/{self.feedback_id}/{filename}"

    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("Обратная связь"),
    )
    file = models.FileField("файл", upload_to=upload_to_path)

    class Meta:
        verbose_name = _("Файл обратной связи")
        verbose_name_plural = _("Файлы обратной связи")
