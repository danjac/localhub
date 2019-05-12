from django.contrib import admin


from communikit.content.admin import PostAdmin
from communikit.events.models import Event


@admin.register(Event)
class EventAdmin(PostAdmin):
    pass
