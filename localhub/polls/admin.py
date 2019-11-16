from django.contrib import admin

from localhub.activities.admin import ActivityAdmin
from localhub.polls.models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
