from django.contrib import admin


from communikit.comments.models import Comment
from communikit.core.markdown.admin import MarkdownFieldMixin


@admin.register(Comment)
class CommentAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = ("owner", "community", "created")
    ordering = ("-created",)

    def community(self, obj: Comment) -> str:
        return obj.activity.community.name
