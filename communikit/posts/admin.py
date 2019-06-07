from django.contrib import admin

from communikit.activities.admin import ActivityAdmin
from communikit.posts.models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
