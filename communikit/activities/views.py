from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities import app_settings
from communikit.activities.models import Activity
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.types import ContextDict


class ActivityQuerySetMixin(CommunityRequiredMixin):
    select_subclasses = True

    def get_queryset(self) -> QuerySet:
        qs = Activity.objects.filter(
            community=self.request.community
        ).select_related("owner", "community")

        if self.select_subclasses:
            qs = qs.select_subclasses()
        return qs


class ActivityStreamView(ActivityQuerySetMixin, ListView):
    template_name = "activities/stream.html"
    paginate_by = app_settings.COMMUNIKIT_ACTIVITIES_PAGE_SIZE
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(community=self.request.community)
            .annotate(num_likes=Count("likes"), num_comments=Count("comment"))
            .order_by("-created")
        )


activity_stream_view = ActivityStreamView.as_view()


class ActivityDetailRouterView(SingleObjectMixin, RedirectView):
    """
    In cases where we don't know the subclass of an activity ahead of time,
    or where it is too inefficient to do so, this will look up the
    correct subclass (post, event etc) and redirect to the correct absolute
    url for that subclass.
    """

    def get_queryset(self) -> QuerySet:
        return Activity.objects.select_subclasses()

    def get_redirect_url(self):
        return self.get_object().get_absolute_url()


activity_detail_router_view = ActivityDetailRouterView.as_view()


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
    ActivityQuerySetMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")


class BaseActivityDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    DeleteView,
):
    permission_required = "activities.delete_activity"
    success_url = reverse_lazy("activities:stream")
    success_message = None

    def get_success_message(self):
        return self.success_message

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class BaseActivityDetailView(ActivityQuerySetMixin, DetailView):
    def get_comments(self) -> QuerySet:
        return (
            self.object.comment_set.select_related(
                "owner", "activity", "activity__community"
            )
            .annotate(num_likes=Count("likes"))
            .order_by("created")
        )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_likes=Count("likes"), num_comments=Count("comment"))
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["comments"] = self.get_comments()
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data
