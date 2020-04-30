from django.contrib import admin

from localhub.apps.activities.admin import ActivityAdmin

from .models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
