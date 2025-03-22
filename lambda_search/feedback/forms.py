from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from feedback.models import Feedback, FeedbackFile, UserInfo

__all__ = ()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if len(data) > 10:
            raise ValidationError(_("Можно загрузить максимум 10 файлов."))

        total_size = sum(f.size for f in data)
        max_total_size = 20 * 1024 * 1024  # 20 MB
        if total_size > max_total_size:
            raise ValidationError(
                _("Общий размер файлов не должен превышать 20 MB."))

        return data


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
    )

    def __init__(self, *args, **kwargs):
        super(FilesForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = FeedbackFile
        exclude = (FeedbackFile.feedback.field.name,)


class UserForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=False,
        help_text=_("Введите ваше имя"),
        label=_("Имя"),
        widget=forms.TextInput(attrs={"placeholder": _("Введите имя")}),
    )
    mail = forms.EmailField(
        required=True,
        help_text=_("Введите вашу почту"),
        label=_("Почта"),
        widget=forms.EmailInput(attrs={"placeholder": _("Введите почту")}),
    )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = UserInfo
        exclude = (UserInfo.user.field.name, UserInfo.user_info.field.name)
