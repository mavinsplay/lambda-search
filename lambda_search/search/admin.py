from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from search.models import Data, ManagedDatabase

__all__ = ()


@admin.register(ManagedDatabase)
class ManagedDatabaseAdmin(admin.ModelAdmin):

    list_display = (
        ManagedDatabase.name.field.name,
        ManagedDatabase.file.field.name,
        ManagedDatabase.active.field.name,
        "progress_bar",
        "related_objects_count",
    )
    list_editable = (ManagedDatabase.active.field.name,)
    search_fields = (ManagedDatabase.name.field.name,)
    list_filter = (ManagedDatabase.active.field.name,)
    readonly_fields = (
        ManagedDatabase.created_at.field.name,
        ManagedDatabase.updated_at.field.name,
    )
    fields = (
        ManagedDatabase.name.field.name,
        ManagedDatabase.file.field.name,
        ManagedDatabase.is_encrypted.field.name,
        ManagedDatabase.active.field.name,
        ManagedDatabase.history.field.name,
        ManagedDatabase.created_at.field.name,
        ManagedDatabase.updated_at.field.name,
    )

    def progress_bar(self, obj):
        if not obj.progress_task_id:
            return _("Не начато")

        from django_celery_results.models import TaskResult

        try:
            task_result = TaskResult.objects.get(task_id=obj.progress_task_id)
            result_data = task_result.result

            if not result_data:
                return _("Ожидание...")

            progress_data = task_result.result
            if isinstance(progress_data, str):
                import json

                progress_data = json.loads(progress_data)

            progress = progress_data.get("percent", 0)
            current = progress_data.get("current", 0)
            total = progress_data.get("total", 0)
            description = progress_data.get(
                "description",
                "",
            )

            color = (
                "#28a745"
                if progress == 100
                else "#007bff" if progress > 0 else "#ffc107"
            )

            return format_html(
                """
                <div class="progress-container" data-task-id="{}">
                    <div style="width: 300px; background-color: #f8f9fa; border-radius: 4px; height: 20px;">
                        <div class="progress-bar-fill" style="width: {}%; background-color: {}; height: 100%; border-radius: 4px; 
                        transition: width 0.3s ease-in-out;"></div>
                    </div>
                    <span class="progress-text">{}% ({}/{})</span>
                    <span style="color: #666; margin-left: 10px;">{}</span>
                </div>
                """,  # noqa: E501, W291
                obj.progress_task_id,
                progress,
                color,
                progress,
                current,
                total,
                description,
            )
        except TaskResult.DoesNotExist:
            return _("Задача не найдена")
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return _("Ошибка данных") + str(e)

    progress_bar.short_description = _("Прогресс")
    progress_bar.allow_tags = True

    def related_objects_count(self, obj):
        """Подсчет количества связанных объектов для базы данных"""
        return obj.data.count()

    related_objects_count.short_description = _("Количество записей")
    related_objects_count.admin_order_field = "data__count"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(data__count=Count("data"))

    class Media:
        css = {
            "all": ("css/progress.css",),
        }
        js = ("js/progress.js",)

    def get_deleted_objects(self, objs, request):
        collector = NestedObjects(using=router.db_for_write(self.model))
        collector.collect(objs)
        related_objects_count = sum(len(v) for v in collector.data.values())
        return (
            [],
            {_("Количество связанных объектов"): related_objects_count},
            set(),
            [],
        )


@admin.register(Data)
class DataDatabaseAdmin(admin.ModelAdmin):
    list_display = (
        Data.user_index.field.name,
        Data.database.field.name,
        Data.column_name.field.name,
        Data.value.field.name,
    )
    ordering = (
        Data.database.field.name,
        Data.user_index.field.name,
    )
