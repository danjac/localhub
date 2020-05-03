from django.contrib import admin

from social_bfg.apps.activities.admin import ActivityAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
