from django.contrib import admin


from communikit.core.markdown.admin import MarkdownFieldMixin


class ActivityAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = ("__str__", "owner", "community", "created")
    ordering = ("-created",)
