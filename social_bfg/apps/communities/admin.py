# Django
from django.contrib import admin

# Social-BFG
from social_bfg.common.markdown.admin import MarkdownFieldMixin

# Local
from .models import Community, Membership


@admin.register(Community)
class CommunityAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    search_fields = ("domain", "name")
    list_display = (
        "domain",
        "name",
        "active",
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("community", "member", "role")
    list_filter = ("active", "role")
    search_fields = ("community__name", "member__username", "member__email")
    raw_id_fields = ("member",)
