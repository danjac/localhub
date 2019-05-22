from django.urls import reverse_lazy

from communikit.activities.views import (
    BaseActivityCreateView,
    BaseActivityDeleteView,
    BaseActivityDetailView,
    BaseActivityDislikeView,
    BaseActivityLikeView,
    BaseActivityListView,
    BaseActivityUpdateView,
)
from communikit.events.forms import EventForm
from communikit.events.models import Event


class EventCreateView(BaseActivityCreateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy("events:list")


event_create_view = EventCreateView.as_view()


class EventListView(BaseActivityListView):
    model = Event


event_list_view = EventListView.as_view()


class EventDetailView(BaseActivityDetailView):
    model = Event


event_detail_view = EventDetailView.as_view()


class EventUpdateView(BaseActivityUpdateView):
    model = Event
    form_class = EventForm


event_update_view = EventUpdateView.as_view()


class EventDeleteView(BaseActivityDeleteView):
    model = Event
    success_url = reverse_lazy("events:list")


event_delete_view = EventDeleteView.as_view()


class EventLikeView(BaseActivityLikeView):
    model = Event


event_like_view = EventLikeView.as_view()


class EventDislikeView(BaseActivityDislikeView):
    model = Event


event_dislike_view = EventDislikeView.as_view()
