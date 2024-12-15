from django import forms

__all__ = ()


class SearchForm(forms.Form):  # TODO
    search_query = forms.CharField(
        required=True,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введите запрос...",
                "class": "form-control rounded-end-0",
            },
        ),
    )
