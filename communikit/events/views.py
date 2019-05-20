# # from django.utils.translation import ugettext_lazy as _

from communikit.activities.views import (
    BaseActivityCreateView,
    BaseActivityDeleteView,
    BaseActivityDetailView,
    BaseActivityDislikeView,
    BaseActivityLikeView,
    BaseActivityUpdateView,
)
from communikit.events.forms import EventForm
from communikit.events.models import Event

# TBD: ListView, calendar view


class EventCreateView(BaseActivityCreateView):
    model = Event
    form_class = EventForm


event_create_view = EventCreateView.as_view()


class EventDetailView(BaseActivityDetailView):
    model = Event


event_detail_view = EventDetailView.as_view()


class EventUpdateView(BaseActivityUpdateView):
    model = Event
    form_class = EventForm


event_update_view = EventUpdateView.as_view()


class EventDeleteView(BaseActivityDeleteView):
    model = Event


event_delete_view = EventDeleteView.as_view()


class EventLikeView(BaseActivityLikeView):
    model = Event


event_like_view = EventLikeView.as_view()


class EventDislikeView(BaseActivityDislikeView):
    model = Event


event_dislike_view = EventDislikeView.as_view()
