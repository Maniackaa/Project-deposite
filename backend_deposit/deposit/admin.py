from django.contrib import admin

from deposit.models import Incoming, BadScreen, Deposit


class IncomingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'register_date', 'response_date', 'recipient', 'sender', 'pay', 'transaction', 'confirmed_deposit', 'type', 'image', 'worker'
    )
    list_filter = ('register_date', 'worker', 'type')


class BadScreenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'incoming_time', 'transaction', 'type', 'image', 'worker', 'size'
    )


class DepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'register_time', 'change_time', 'uid', 'phone', 'pay_sum', 'input_transaction', 'status', 'pay_screen', 'confirmed_incoming')
    list_filter = ('register_time', 'status')
    list_editable = ('status',)
    # radio_fields = {'status': admin.VERTICAL}


admin.site.register(Incoming, IncomingAdmin)
admin.site.register(BadScreen, BadScreenAdmin)
admin.site.register(Deposit, DepositAdmin)
