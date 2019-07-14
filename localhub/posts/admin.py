from django.contrib import admin

from localhub.activities.admin import ActivityAdmin
from localhub.posts.models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
