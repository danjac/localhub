from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities import app_settings
from communikit.activities.models import Activity
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.types import ContextDict


class ActivityStreamView(CommunityRequiredMixin, ListView):
    template_name = "activities/stream.html"
    paginate_by = app_settings.COMMUNIKIT_ACTIVITIES_PAGE_SIZE
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            Activity.objects.filter(community=self.request.community)
            .annotate(num_likes=Count("likes"), num_comments=Count("comment"))
            .select_related("community", "owner")
            .order_by("-created")
            .select_subclasses()
        )


activity_stream_view = ActivityStreamView.as_view()


class BaseActivityCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    permission_required = "activities.create_activity"
    success_url = reverse_lazy("activities:stream")
    success_message = _("Your update has been posted")

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_success_message(self) -> str:
        return self.success_message

    def form_valid(self, form) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class BaseActivityUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")


class BaseActivityDetailView(DetailView):
    def get_comments(self) -> QuerySet:
        return (
            self.object.comment_set.select_related(
                "owner", "post", "post__community"
            )
            .annotate(num_likes=Count("likes"))
            .order_by("created"),
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["comments"] = self.get_comments()
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data
