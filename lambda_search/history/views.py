from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponseForbidden
from history.models import QueryHistory
from datetime import timedelta
from django.utils.timezone import now


__all__ = ()


class HistoryView(ListView):
    """
    Представление для отображения истории запросов.
    """

    model = QueryHistory
    template_name = "history/history.html"
    context_object_name = "queries"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created_at")
        for query in queryset:
            query.can_repeat = (now() - query.created_at) <= timedelta(days=1)

        return queryset

    def post(self, request, *args, **kwargs):
        """
        Повторение запроса.
        """
        query_id = request.POST.get("query_id")
        if query_id:
            history = QueryHistory.objects.filter(id=query_id).first()
            if history:
                time_elapsed = now() - history.created_at
                if time_elapsed > timedelta(days=1):
                    return HttpResponseForbidden(
                        "Время для повторения запроса истекло.",
                    )

                return JsonResponse({"result": history.result})

        return self.get(request, *args, **kwargs)


class HistoryDetailView(DetailView):
    """
    Детальное представление для истории запроса.
    """

    model = QueryHistory
    template_name = "history/history_detail.html"
    context_object_name = "query"
