from django.contrib import admin

from .models import Attempt, Client, Mailing, Message

admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Mailing)
admin.site.register(Attempt)
