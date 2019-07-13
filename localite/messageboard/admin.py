from django.contrib import admin

from localite.messageboard.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ("sender",)
    search_fields = ("subject", "message", "sender__email", "sender__username")
    list_display = ("subject", "created", "sender", "community")
