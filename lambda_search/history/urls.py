from django.contrib.auth.decorators import login_required
from django.urls import path

from history.views import HistoryDetailView, HistoryView, QueryDeleteView

app_name = "history"

urlpatterns = [
    path("", HistoryView.as_view(), name="history"),
    path("<int:pk>/", HistoryDetailView.as_view(), name="history-detail"),
    path("delete/<int:pk>/", QueryDeleteView.as_view(), name="history-delete"),
]
