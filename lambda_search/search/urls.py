from django.urls import path

from search.admin import ManagedDatabaseAdmin
from search.views import SearchView, TaskProgressView

app_name = "search"

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("task-progress/", TaskProgressView.as_view(), name="task_progress"),
    path(
        "admin/search/manageddatabase/upload-progress/",
        ManagedDatabaseAdmin.get_upload_progress,
        name="upload_progress",
    ),
]
