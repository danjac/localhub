from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from markdownx.admin import MarkdownxModelAdmin

from communikit.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(MarkdownxModelAdmin):
    raw_id_fields = ("author",)
    list_display = ("author", "community", "created")
    search_fields = (
        "content",
        "author__username",
        "author__email",
        "post__title",
        "post__description",
        "post__community__name",
    )

    def community(self, obj):
        return obj.post.community

    def get_queryset(self, request: HttpRequest) -> HttpResponse:
        return (
            super()
            .get_queryset(request)
            .select_related("post", "author", "post__community")
        )
