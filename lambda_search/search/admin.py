import sqlite3

from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from search.models import ManagedDatabase


__all__ = ()


@admin.register(ManagedDatabase)
class ManagedDatabaseAdmin(admin.ModelAdmin):
    """Админка для управления базами данных."""

    list_display = ("name", "active", "file", "view_content_button")
    list_editable = ("active",)
    search_fields = ("name",)
    list_filter = ("active",)
    readonly_fields = ("created_at", "updated_at")
    fields = ("name", "file", "active", "history", "created_at", "updated_at")

    def get_urls(self):
        """Добавляем кастомный URL для просмотра содержимого базы."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:db_id>/view-content/",
                self.admin_site.admin_view(self.view_database_content),
                name="view_database_content",
            ),
        ]
        return custom_urls + urls

    def view_content_button(self, obj):
        """Добавляет кнопку для просмотра содержимого базы."""
        return format_html(
            (
                f"<a class='button' href='{obj.id}/view-content/'>"
                f"{_('Просмотреть содержимое')}</a>"
            ),
        )

    view_content_button.short_description = _("Содержимое")
    view_content_button.allow_tags = True

    def view_database_content(self, request, db_id):
        """Просмотр содержимого базы данных."""
        database = ManagedDatabase.objects.get(id=db_id)
        db_path = database.file.path

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';",
                )
                tables = cursor.fetchall()

                table_data = {}
                for (table_name,) in tables:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    table_data[table_name] = {"columns": columns, "rows": rows}

            context = {
                "database": database,
                "table_data": table_data,
            }
            return render(request, "admin/view_database.html", context)
        except sqlite3.Error as e:
            return render(
                request,
                "admin/error.html",
                {"error_message": _(f"Ошибка при открытии базы: {str(e)}")},
            )
