from django.contrib import admin

from communikit.communities.models import Community


class CommunityAdmin(admin.ModelAdmin):
    search_fields = ("domain", "name")
    list_display = ("domain", "name", "active")


admin.site.register(Community, CommunityAdmin)
