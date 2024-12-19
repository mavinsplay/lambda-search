from django.contrib import admin

from feedback.models import Feedback, FeedbackFile, StatusLog, UserInfo

__all__ = ()


class FeedbackFileInline(admin.TabularInline):
    model = FeedbackFile
    extra = 0
    fields = (FeedbackFile.file.field.name,)


class UserInfoInline(admin.StackedInline):
    model = UserInfo
    extra = 0
    fields = (
        UserInfo.name.field.name,
        UserInfo.mail.field.name,
    )


class StatusLogInline(admin.TabularInline):
    model = StatusLog
    extra = 0
    fields = (
        StatusLog.user.field.name,
        StatusLog.timestamp.field.name,
        StatusLog.from_status.field.name,
        StatusLog.to.field.name,
    )
    readonly_fields = (
        StatusLog.user.field.name,
        StatusLog.timestamp.field.name,
        StatusLog.from_status.field.name,
        StatusLog.to.field.name,
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        Feedback.text.field.name,
        Feedback.created_on.field.name,
        Feedback.status.field.name,
    )
    list_filter = (Feedback.status.field.name, Feedback.created_on.field.name)
    search_fields = (
        Feedback.text.field.name,
        f"{UserInfo._meta.model_name}__{UserInfo.name.field.name}",
        f"{UserInfo._meta.model_name}__{UserInfo.mail.field.name}",
    )
    inlines = [UserInfoInline, FeedbackFileInline, StatusLogInline]
    readonly_fields = (Feedback.created_on.field.name,)

    def save_model(self, request, obj, form, change):
        if change:
            previous_status = obj.status
            if obj.status != previous_status:
                StatusLog.objects.create(
                    feedback=obj,
                    user=request.user,
                    from_status=previous_status,
                    to=obj.status,
                )

        super().save_model(request, obj, form, change)


class StatusLogAdmin(admin.ModelAdmin):
    list_display = (
        StatusLog.feedback.field.name,
        StatusLog.timestamp.field.name,
        StatusLog.from_status.field.name,
        StatusLog.to.field.name,
    )
    list_filter = (
        StatusLog.from_status.field.name,
        StatusLog.to.field.name,
        StatusLog.timestamp.field.name,
    )
    search_fields = (
        f"{Feedback._meta.model_name}__{Feedback.text.field.name}",
        f"{UserInfo._meta.model_name}__{UserInfo.user.field.name}",
    )
    readonly_fields = (
        StatusLog.feedback.field.name,
        StatusLog.timestamp.field.name,
        StatusLog.from_status.field.name,
        StatusLog.to.field.name,
    )


class UserInfoAdmin(admin.ModelAdmin):
    list_display = (
        UserInfo.name.field.name,
        UserInfo.mail.field.name,
        "user_info",
    )
    search_fields = (
        UserInfo.name.field.name,
        UserInfo.mail.field.name,
        f"{UserInfo._meta.model_name}__{UserInfo.user.field.name}",
    )
    list_filter = (UserInfo.user.field.name,)


class FeedbackFileAdmin(admin.ModelAdmin):
    list_display = (
        FeedbackFile.feedback.field.name,
        FeedbackFile.file.field.name,
    )
    search_fields = (
        f"{Feedback._meta.model_name}__{Feedback.text.field.name}",
    )
    readonly_fields = (FeedbackFile.file.field.name,)


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(StatusLog, StatusLogAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(FeedbackFile, FeedbackFileAdmin)
