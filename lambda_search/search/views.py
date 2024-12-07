from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from search.forms import SearchForm
from search.models import UnifiedDatabase


__all__ = ()


class SearchView(FormView):
    template_name = "search/search.html"
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data["search_query"]
        search_results = UnifiedDatabase.objects.search(query)
        formatted_results = self.format_results(search_results)

        return self.render_to_response(
            self.get_context_data(results=formatted_results),
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(
                results=None,
                errors=form.errors,
            ),
        )

    def format_results(self, raw_results):
        unique_databases = self._merge_results_by_database(raw_results)
        formatted_results = []

        for database, data in unique_databases.items():
            formatted_results.append(
                {
                    "database": database,
                    "history": data["history"],
                    "data": self._categorize_data(data["columns"]),
                },
            )

        return formatted_results

    def _merge_results_by_database(self, raw_results):
        """
        Объединяет результаты по уникальным базам данных.
        """
        merged_results = {}

        for entry in raw_results:
            database = entry.get("database", "Неизвестно")
            results = entry.get("results", [])

            if database not in merged_results:
                merged_results[database] = {
                    "history": None,
                    "columns": set(),
                }

            for result in results:
                if not merged_results[database]["history"]:
                    merged_results[database]["history"] = result.get(
                        "history",
                        "История отсутствует",
                    )

                merged_results[database]["columns"].update(
                    result.get("columns", []),
                )

        return merged_results

    def _categorize_data(self, columns):
        """
        Классифицирует данные по уровням критичности (critical, medium, low)
        с учётом нормализации названий.
        """
        danger_levels = {
            "critical": {
                "password",
                "email",
                "phone_number",
                "credit_card",
                "card_number",
                "cvv",
                "address",
                "bank_account",
            },
            "medium": {
                "birth_date",
                "work_address",
                "city",
                "name",
                "zip",
                "postal_code",
            },
            "low": set(),
        }

        normalized_columns = self._normalize_column_names(columns)

        categorized_data = {"critical": [], "medium": [], "low": []}
        for column in normalized_columns:
            if column in danger_levels["critical"]:
                categorized_data["critical"].append(column)
            elif column in danger_levels["medium"]:
                categorized_data["medium"].append(column)
            else:
                categorized_data["low"].append(column)

        return categorized_data

    def _normalize_column_names(self, columns):
        """
        Приводит названия колонок к единообразному внутреннему формату.
        """
        normalization_map = {
            "email": "email",
            "почта": "email",
            "номер телефона": "phone_number",
            "phone number": "phone_number",
            "number": "phone_number",
            "телефон": "phone_number",
            "password": "password",
            "пароль": "password",
            "credit card": "credit_card",
            "банковская карта": "credit_card",
            "birthdate": "birth_date",
            "дата рождения": "birth_date",
            "датарожд": "birth_date",
            "address": "address",
            "адрес": "address",
            "city": "city",
            "город": "city",
            "имя": "name",
        }

        return [
            normalization_map.get(col.strip().lower(), col) for col in columns
        ]

    def _translate_column_names(self, columns):
        translation_map = {
            "email": _("Email"),
            "phone_number": _("Телефон"),
            "password": _("Пароль"),
            "credit_card": _("Банковская карта"),
            "birth_date": _("Дата рождения"),
            "address": _("Адрес"),
            "city": _("Город"),
            "name": _("Имя"),
        }

        return [translation_map.get(col, col) for col in columns]
