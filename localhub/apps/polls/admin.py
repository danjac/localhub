# Django
from django.contrib import admin

# Localhub
# Social-BFG
from localhub.apps.activities.admin import ActivityAdmin

# Local
from .models import Poll


@admin.register(Poll)
class PostAdmin(ActivityAdmin):
    ...
