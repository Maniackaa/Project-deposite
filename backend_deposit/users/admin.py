from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "role", "is_admin", "is_staff")

    list_filter = (
        "username",
        "email",
    )
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
