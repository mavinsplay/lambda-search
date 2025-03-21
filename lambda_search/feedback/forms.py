from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from feedback.models import Feedback, FeedbackFile, UserInfo

__all__ = ()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]

        return [single_file_clean(data, initial)]


def validate_file_size(value):
    max_file_size = 20 * 1024 * 1024  # 20 MB
    if value.size > max_file_size:
        raise ValidationError(
            _("Общий размер файлов не должен превышать 20 MB."),
        )


class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.name == "turnstile":
                continue

            field.field.widget.attrs["class"] = "form-control"

    if settings.CAPTCHA_ENABLED:
        from turnstile.fields import TurnstileField

        turnstile = TurnstileField()

    class Meta:
        model = Feedback
        exclude = (
            Feedback.created_on.field.name,
            Feedback.status.field.name,
            Feedback.author.field.name,
        )
        help_texts = {
            "text": _("Напишите ваш отзыв"),
        }
        labels = {
            "text": _("Отзыв"),
        }
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "placeholder": _("Напишите ваш отзыв"),
                    "rows": 10,
                },
            ),
        }


class FilesForm(forms.ModelForm):
    files = MultipleFileField(
        label=_("Файлы"),
        required=False,
        help_text=_("Добавьте файлы для лучшего понимания проблемы"),
        validators=[validate_file_size],
    )

    def __init__(self, *args, **kwargs):
        super(FilesForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = FeedbackFile
        exclude = (
            FeedbackFile.feedback.field.name,
        )


class UserForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=False,
        help_text=_("Введите ваше имя"),
        label=_("Имя"),
    )
    mail = forms.EmailField(
        required=True,
        help_text=_("Введите вашу почту"),
        label=_("Почта"),
    )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = UserInfo
        exclude = (UserInfo.user.field.name, UserInfo.user_info.field.name)
