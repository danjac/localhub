from django.contrib import admin

from bfg.apps.activities.admin import ActivityAdmin

from .models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
