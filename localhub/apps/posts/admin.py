# Django
from django.contrib import admin

# Localhub
# Social-BFG
from localhub.apps.activities.admin import ActivityAdmin

# Local
from .models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
