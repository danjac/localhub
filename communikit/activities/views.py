from django.db.models import Count, QuerySet
from django.views.generic import ListView

# from communikit.activities import app_settings
from communikit.activities.models import Activity
from communikit.communities.views import CommunityRequiredMixin


class ActivityStreamView(CommunityRequiredMixin, ListView):
    template_name = "activities/stream.html"
    paginate_by = 15  # TBD add to settings
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            Activity.objects.filter(community=self.request.community)
            .annotate(num_likes=Count("likes"))
            .annotate(num_comments=Count("comment"))
            .select_related("community", "owner")
            .order_by("-created")
            .select_subclasses()
        )


activity_stream_view = ActivityStreamView.as_view()
