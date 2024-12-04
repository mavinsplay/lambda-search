from django.contrib import admin
from search.models import ManagedDatabase

__all__ = ()


@admin.register(ManagedDatabase)
class ManagedDatabaseAdmin(admin.ModelAdmin):
    """Админка для управления базами данных."""

    list_display = ("name", "active", "file")
    list_editable = ("active",)
    search_fields = ("name",)
    list_filter = ("active",)
    fields = ("name", "file", "active")
