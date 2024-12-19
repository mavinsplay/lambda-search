from django.contrib.auth.decorators import login_required
from django.urls import path

from history.views import HistoryDetailView, HistoryView


app_name = "history"

urlpatterns = [
    path("", login_required(HistoryView.as_view()), name="history"),
    path(
        "<int:pk>/",
        login_required(HistoryDetailView.as_view()),
        name="history-detail",
    ),
]
