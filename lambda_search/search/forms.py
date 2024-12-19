import re

from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

__all__ = ("SearchForm",)


def normalize_search_query(value):
    """
    Нормализует значение search_query.
    - Убирает лишние символы из номера телефона, приводя к формату 79111411123.
    - Убирает теги и лишние символы из электронной почты.
    """
    if re.fullmatch(r"[\+\(\)\-\d\s]+", value):
        normalized = re.sub(r"[\D]+", "", value)
        if normalized.startswith("8"):
            return "7" + normalized[1:]

        return normalized

    if "@" in value:
        return re.sub(r"<[^>]*>", "", value)

    return value


def validate_length(value):
    """Проверка длины значения."""
    if not (8 <= len(value) <= 100):
        raise ValidationError(
            _("Длина запроса должна быть от 8 до 100 символов."),
        )


class SearchForm(forms.Form):
    captcha = CaptchaField()
    search_query = forms.CharField(
        required=True,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Введите запрос..."),
                "class": "form-control",
                "minlength": 8,
                "maxlength": 100,
            },
        ),
        validators=[validate_length],
    )

    def clean_search_query(self):
        """Нормализация и очистка поля search_query."""
        data = self.cleaned_data["search_query"]
        return normalize_search_query(data)
