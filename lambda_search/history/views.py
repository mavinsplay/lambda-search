from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView

from history.models import QueryHistory
from search.encryptor import CellEncryptor

__all__ = ()


class HistoryView(LoginRequiredMixin, ListView):
    """
    Представление для отображения истории запросов конкретного пользователя.
    """

    model = QueryHistory
    template_name = "history/history.html"
    context_object_name = "queries"
    key = settings.ENCRYPTION_KEY
    paginate_by = 9
    encryptor = CellEncryptor(key)

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .order_by(f"-{QueryHistory.created_at.field.name}")
        )
        for query in queryset:
            query.can_repeat = (now() - query.created_at) >= timedelta(days=1)
            query.query = self.encryptor.decrypt(query.query)

        return queryset

    def post(self, request, *args, **kwargs):
        """
        Повторение запроса.
        """
        query_id = request.POST.get("query_id")
        if query_id:
            history = QueryHistory.objects.filter(
                id=query_id,
                user=request.user,
            ).first()
            if history:
                time_elapsed = now() - history.created_at
                if time_elapsed < timedelta(days=1):
                    return HttpResponseForbidden(
                        "Время для повторения запроса истекло.",
                    )

                return redirect(f"/search?search_query={history.query}")

        return self.get(request, *args, **kwargs)


class HistoryDetailView(DetailView):
    """
    Детальное представление для истории запроса конкретного пользователя.
    """

    key = settings.ENCRYPTION_KEY
    encryptor = CellEncryptor(key)
    model = QueryHistory
    template_name = "history/history_detail.html"
    context_object_name = "query"

    def get_queryset(self):
        """
        Ограничение доступа к записям только для текущего пользователя.
        """
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"].query = self.encryptor.decrypt(context["query"].query)
        return context


class QueryDeleteView(SuccessMessageMixin, DeleteView):
    model = QueryHistory
    success_url = reverse_lazy("history:history")
    success_message = _("Запрос успешно удалён.")
