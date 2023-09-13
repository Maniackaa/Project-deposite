from django.contrib import admin

from deposit.models import Incoming, BadScreen

admin.site.register(Incoming)
admin.site.register(BadScreen)
