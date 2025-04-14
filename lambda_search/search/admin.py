from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.core.cache import cache
from django.db import router
from django.http import JsonResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from search.models import Data, ManagedDatabase, models
from search.widgets import ProgressBarFileInput

__all__ = ()


@admin.register(ManagedDatabase)
class ManagedDatabaseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.FileField: {"widget": ProgressBarFileInput},
    }

    class Media:
        css = {
            "all": (
                "css/progress.css",
                "css/file_upload_progress.css",
            ),
        }
        js = (
            "js/progress.js",
            "js/file_upload_progress.js",
            "admin/js/jquery.init.js",  # Добавляем jQuery
        )

    list_display = (
        ManagedDatabase.name.field.name,
        ManagedDatabase.file.field.name,
        ManagedDatabase.active.field.name,
        "progress_bar",
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

    def response_add(self, request, obj, form=None, post_url_continue=None):
        """Переопределяем метод для возврата JSON при AJAX запросе"""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            if form and form.errors:
                return JsonResponse(
                    {
                        "status": "error",
                        "errors": {
                            field: [str(error) for error in errors]
                            for field, errors in form.errors.items()
                        },
                    },
                )

            return JsonResponse(
                {
                    "status": "success",
                    "redirect_url": request.path.rsplit("/", 2)[0] + "/",
                    "message": "База данных успешно загружена",
                },
            )

        return super().response_add(request, obj, form, post_url_continue)

    def response_change(self, request, obj, form=None):
        """Переопределяем метод для возврата JSON при AJAX запросе"""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            if form and form.errors:
                return JsonResponse(
                    {
                        "status": "error",
                        "errors": {
                            field: [str(error) for error in errors]
                            for field, errors in form.errors.items()
                        },
                    },
                )

            return JsonResponse(
                {
                    "status": "success",
                    "redirect_url": request.path.rsplit("/", 2)[0] + "/",
                    "message": "База данных успешно обновлена",
                },
            )

        return super().response_change(request, obj, form)

    def get_upload_progress(self, request):
        """Метод для получения прогресса загрузки через Redis"""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                key = request.GET.get("X-Progress-ID")
                if key:
                    cache_key = f"upload_progress_{key}"
                    data = cache.get(cache_key)
                    if data:
                        return JsonResponse(data)

                    return JsonResponse(
                        {
                            "status": "unknown",
                            "message": "Данные о прогрессе не найдены",
                        },
                    )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Ошибка получения прогресса: {str(e)}",
                    },
                )

        return JsonResponse(
            {"status": "error", "message": "Недопустимый запрос"},
        )

    def save_model(self, request, obj, form, change):
        """Сохранение прогресса загрузки в Redis"""
        if "file" in form.changed_data:
            progress_id = request.POST.get("X-Progress-ID")
            if progress_id:
                cache_key = f"upload_progress_{progress_id}"
                cache.set(
                    cache_key,
                    {"status": "processing", "progress": 0, "speed": 0},
                    timeout=3600,
                )

        super().save_model(request, obj, form, change)


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
