from django.contrib import admin

from history.models import QueryHistory

__all__ = ()


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        QueryHistory.id.field.name,
        QueryHistory.user.field.name,
        QueryHistory.query.field.name,
        QueryHistory.created_at.field.name,
        "result_summary",
    )
    list_filter = (
        QueryHistory.user.field.name,
        QueryHistory.created_at.field.name,
    )
    search_fields = ("user__username", "query")
    list_per_page = 20

    def result_summary(self, obj):
        return str(obj.result)[:100] + (
            "..." if len(str(obj.result)) > 100 else ""
        )

    result_summary.short_description = QueryHistory.result.field.name

    part1 = (
        None,
        {
            "fields": (
                QueryHistory.user.field.name,
                QueryHistory.query.field.name,
                QueryHistory.created_at.field.name,
            ),
        },
    )
    part2 = (
        "Results",
        {
            "fields": (QueryHistory.result.field.name,),
            "classes": ("collapse",),
        },
    )
    fieldsets = (part1, part2)

    readonly_fields = (QueryHistory.created_at.field.name,)
