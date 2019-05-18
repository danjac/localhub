from django.core.paginator import Page
from django.views.generic import TemplateView


from communikit.activities import app_settings
from communikit.activities.models import activity_stream
from communikit.communities.views import CommunityRequiredMixin
from communikit.events.models import Event
from communikit.posts.models import Post
from communikit.types import ContextDict

# TBD: search activities, per-user activities


class ActivityStreamView(CommunityRequiredMixin, TemplateView):
    template_name = "activities/stream.html"

    def get_paginator_kwargs(self) -> ContextDict:
        try:
            page_number = int(self.request.GET["page"])
        except (KeyError, ValueError):
            page_number = 1

        return {
            "page_number": page_number,
            "page_size": app_settings.ACTIVITY_PAGE_SIZE,
            "allow_empty_first_page": True,
        }

    def get_activity_stream(self) -> Page:
        return activity_stream(
            {
                "post": Post.objects.filter(community=self.request.community),
                "event": Event.objects.filter(
                    community=self.request.community
                ),
            },
            **self.get_paginator_kwargs(),
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        page = self.get_activity_stream()
        data.update(
            {
                "paginator": page.paginator,
                "page_obj": page,
                "object_list": page.object_list,
                "is_paginated": page.has_other_pages(),
            }
        )
        return data
