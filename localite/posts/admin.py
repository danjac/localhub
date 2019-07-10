from django.contrib import admin

from localite.activities.admin import ActivityAdmin
from localite.posts.models import Post


@admin.register(Post)
class PostAdmin(ActivityAdmin):
    ...
