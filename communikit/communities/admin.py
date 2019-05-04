from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from communikit.communities.models import Community, Membership


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    search_fields = ("domain", "name")
    list_display = ("domain", "name", "active")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("community", "member", "role")
    list_filter = ("active", "role")
    search_fields = ("community__name", "member__username", "member__email")
    raw_id_fields = ("member",)

    def get_queryset(self, request: HttpRequest) -> HttpResponse:
        return (
            super().get_queryset(request).select_related("community", "member")
        )
