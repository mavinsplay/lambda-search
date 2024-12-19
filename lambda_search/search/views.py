from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView

from history.models import QueryHistory
from search.encryptor import CellEncryptor
from search.forms import SearchForm
from search.models import Data


__all__ = ()


class SearchView(LoginRequiredMixin, FormView):
    template_name = "search/search.html"
    form_class = SearchForm
    key = settings.ENCRYPTION_KEY
    encryptor = CellEncryptor(key)

    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запроса для предзаполнения формы.
        """
        req = request.GET.get("search_query", "")
        search_query = self.encryptor.decrypt(req) if req else ""
        form = self.form_class(initial={"search_query": search_query})
        return self.render_to_response(
            self.get_context_data(form=form, results=None),
        )

    def form_valid(self, form):
        query = self.encryptor.encrypt(form.cleaned_data["search_query"])
        search_results = Data.objects.search(query)
        formatted_results = self._format_results(search_results)
        QueryHistory.objects.create(
            user=self.request.user,
            query=query,
            result=formatted_results,
        )
        form = self.form_class()
        return self.render_to_response(
            self.get_context_data(results=formatted_results, form=form),
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(
                results=None,
                errors=form.errors,
            ),
        )

    def _format_results(self, raw_results):
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

    def _merge_results_by_database(self, results):
        """
        Группирует результаты по базе данных и собирает соответствующие данные.
        """
        grouped_data = {}

        for item in results:
            db_name = item.database.name

            if db_name not in grouped_data:
                grouped_data[db_name] = {
                    "history": item.database.history,
                    "columns": [],
                }

            grouped_data[db_name]["columns"].append(item.column_name)

        return grouped_data

    def _categorize_data(self, columns):
        """
        Классифицирует данные по уровням критичности (critical, medium, low).
        """
        danger_levels = {
            "critical": {
                "password",
                "email",
                "phone_number",
                "credit_card",
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
                "username",
                "last_name",
            },
            "low": set(),
        }

        normalized_columns = self._normalize_column_names(columns)

        categorized_data = {"critical": [], "medium": [], "low": []}
        for column in normalized_columns:
            if (
                column in danger_levels["critical"]
                and column not in categorized_data["critical"]
            ):
                categorized_data["critical"].append(column)

            elif (
                column in danger_levels["medium"]
                and column not in categorized_data["medium"]
            ):
                categorized_data["medium"].append(column)

            elif column not in categorized_data["low"]:
                categorized_data["low"].append(column)

        return categorized_data

    def _normalize_column_names(self, columns):
        """
        Приводит названия колонок к единообразному формату.
        """
        normalization_map = {
            "email": "email",
            "почта": "email",
            "номер телефона": "phone_number",
            "phone number": "phone_number",
            "phone": "phone_number",
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
            "first_name": "name",
            "фамилия": "last_name",
            "пользователь": "username",
            "профессия": "profession",
            "работа": "job",
            "описание": "description",
        }

        return [
            normalization_map.get(col.strip().lower(), col) for col in columns
        ]
