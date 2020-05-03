# Django
from django.contrib import admin

# Social-BFG
from social_bfg.apps.activities.admin import ActivityAdmin

from .models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
