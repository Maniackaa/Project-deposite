from django.contrib import admin

from deposit.models import Incoming, BadScreen


class IncomingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'register_date', 'response_date', 'recipient', 'sender', 'pay', 'transaction', 'type', 'image', 'worker'
    )


class BadScreenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'transaction', 'type', 'image'
    )


admin.site.register(Incoming, IncomingAdmin)
admin.site.register(BadScreen, BadScreenAdmin)
