from django import forms

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

    class Meta:
        model = Feedback
        exclude = (
            Feedback.created_on.field.name,
            Feedback.status.field.name,
            Feedback.author.field.name,
        )
        help_texts = {
            "text": "Напишите ваш отзыв",
        }
        labels = {
            "text": "Отзыв",
        }
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "placeholder": "Напишите ваш отзыв",
                    "rows": 10,
                },
            ),
        }


class FilesForm(forms.ModelForm):
    files = MultipleFileField(
        label="Файлы",
        required=False,
        help_text="Добавьте файл для лучшего понимания проблемы",
    )

    def __init__(self, *args, **kwargs):
        super(FilesForm, self).__init__(*args, **kwargs)

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
        help_text="Введите ваше имя",
        label="Имя",
    )
    mail = forms.EmailField(
        required=True,
        help_text="Введите вашу почту",
        label="Почта",
    )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserInfo
        exclude = (UserInfo.user.field.name, UserInfo.user_info.field.name)
