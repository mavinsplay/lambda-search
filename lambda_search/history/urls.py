from django.urls import path

from history.views import HistoryDetailView, HistoryView

app_name = "history"

urlpatterns = [
    path("", HistoryView.as_view(), name="history"),
    path("<int:pk>/", HistoryDetailView.as_view(), name="history-detail"),
]
