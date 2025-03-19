import re

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

__all__ = ("SearchForm",)


def normalize_search_query(value):
    if re.fullmatch(r"[\+\(\)\-\d\s]+", value):
        normalized = re.sub(r"[\D]+", "", value)
        if normalized.startswith("8"):
            return "7" + normalized[1:]

        return normalized

    if "@" in value:
        return re.sub(r"<[^>]*>", "", value)

    return value


def validate_length(value):
    if not (8 <= len(value) <= 100):
        raise ValidationError(
            _("Длина запроса должна быть от 8 до 100 символов."),
        )


class SearchForm(forms.Form):
    if settings.CAPTCHA_ENABLED:
        from turnstile.fields import TurnstileField

        turnstile = TurnstileField()

    search_query = forms.CharField(
        required=True,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Введите запрос..."),
                "class": "form-control rounded-end-0",
                "minlength": 8,
                "maxlength": 100,
            },
        ),
        validators=[validate_length],
    )

    def clean_search_query(self):
        data = self.cleaned_data["search_query"]
        return normalize_search_query(data)
