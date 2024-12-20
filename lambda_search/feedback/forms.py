from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import gettext as _

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


class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            if field.name == "captcha":
                continue

            field.field.widget.attrs["class"] = "form-control"

    captcha = CaptchaField()

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
        help_text=_("Добавьте файл для лучшего понимания проблемы"),
    )

    def __init__(self, *args, **kwargs):
        super(FilesForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    class Meta:
        model = FeedbackFile
        exclude = (
            FeedbackFile.feedback.field.name,
            FeedbackFile.file.field.name,
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
