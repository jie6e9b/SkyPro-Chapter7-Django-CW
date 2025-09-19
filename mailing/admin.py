from django.contrib import admin

from .models import Attempt, Client, Mailing, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner")
    search_fields = ("email", "full_name")
    list_filter = ("owner",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "start_time", "end_time", "owner")
    list_filter = ("status", "owner")
    search_fields = ("message__subject",)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "status", "attempt_time", "server_response")
    list_filter = ("status",)
