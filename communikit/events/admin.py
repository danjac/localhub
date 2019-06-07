from django.contrib import admin

from communikit.activities.admin import ActivityAdmin
from communikit.events.models import Event


@admin.register(Event)
class EventAdmin(ActivityAdmin):
    ...
