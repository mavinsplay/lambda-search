from django.contrib import admin, auth
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import get_thumbnail

from users.models import Profile

__all__ = ()

user = auth.get_user_model()


class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = BaseUserAdmin.list_display + ("main_image_thumbnail",)

    def main_image_thumbnail(self, obj):
        if hasattr(obj, "profile") and obj.profile.image:
            thumb = get_thumbnail(
                obj.profile.image,
                "300x300",
                crop="center",
                quality=99,
            )
            return format_html(
                '<img src="{}" width="50" height="50" />',
                thumb.url,
            )

        return ""

    main_image_thumbnail.short_description = _("Profile picture")


admin.site.unregister(user)
admin.site.register(user, UserAdmin)
