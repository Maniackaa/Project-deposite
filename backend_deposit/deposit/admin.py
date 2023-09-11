from django.contrib import admin

# Register your models here.
from deposit.models import Incoming, Screen

admin.site.register(Incoming)
admin.site.register(Screen)
