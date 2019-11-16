from django.contrib import admin

from localhub.activities.admin import ActivityAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
