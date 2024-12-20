from django.conf import settings
import django.core.exceptions
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
        "Создано в",
        auto_now_add=True,
        null=True,
    )
    status = models.CharField(
        "Статус обработки",
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
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратные связи"


class UserInfo(models.Model):
    name = models.CharField("Имя", max_length=100, null=True, blank=True)
    mail = models.EmailField("Почта")
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
        verbose_name="Информация о пользователе",
    )

    class Meta:
        verbose_name = "Информация о пользователе"
        verbose_name_plural = "Информация о пользователях"

    def __str__(self):
        return self.name or "Аноним"


class StatusLog(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="Обратная связь",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    timestamp = models.DateTimeField("Создано в", auto_now_add=True)
    from_status = models.CharField(
        "Из",
        max_length=20,
        choices=Feedback.STATUS_CHOICES,
        db_column="from",
    )
    to = models.CharField(
        "В",
        max_length=20,
        choices=Feedback.STATUS_CHOICES,
        db_column="to",
    )

    class Meta:
        verbose_name = "Лог изменения статуса"
        verbose_name_plural = "Логи изменения статусов"

    def __str__(self):
        return (
            f"Статус изменен с {self.from_status} н"
            f"а {self.to} пользователем {self.user}"
        )


def file_size(value):
    limit = 50 * 1024 * 1024
    if value.size > limit:
        raise django.core.exceptions.ValidationError(
            _("Файл слишком большой, максимум 50 МБ"),
        )


class FeedbackFile(models.Model):
    def upload_to_path(self, filename):
        return f"uploads/{self.feedback_id}/{filename}"

    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Обратная связь",
    )
    file = models.FileField(
        "файл",
        upload_to=upload_to_path,
        validators=[file_size],
    )

    class Meta:
        verbose_name = "Файл обратной связи"
        verbose_name_plural = "Файлы обратной связи"
