# Django
from django.contrib import admin

# Localhub
from localhub.activities.admin import ActivityAdmin

# Local
from .models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
