# Django
from django.contrib import admin

# Localhub
from localhub.activities.admin import ActivityAdmin

# Local
from .models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
