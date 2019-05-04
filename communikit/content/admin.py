from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from markdownx.admin import MarkdownxModelAdmin

from communikit.content.models import Post


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    raw_id_fields = ("author",)
    list_display = ("author", "community", "title", "created")
    search_fields = (
        "community__name",
        "author__username",
        "author__email",
        "title",
        "description",
    )

    def get_queryset(self, request: HttpRequest) -> HttpResponse:
        return (
            super().get_queryset(request).select_related("community", "author")
        )
