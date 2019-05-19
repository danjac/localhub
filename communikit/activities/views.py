from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import QuerySet
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
    View,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities import app_settings
from communikit.activities.models import Activity, Like
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.types import ContextDict


class ActivityQuerySetMixin(CommunityRequiredMixin):
    select_subclass = None

    def get_queryset(self) -> QuerySet:
        qs = Activity.objects.filter(
            community=self.request.community
        ).select_related("owner", "community")

        if self.select_subclass:
            qs = qs.select_subclasses(self.select_subclass)
        else:
            qs = qs.select_subclasses()

        return qs


class BaseActivityListView(ActivityQuerySetMixin, ListView):
    paginate_by = app_settings.COMMUNIKIT_ACTIVITIES_PAGE_SIZE
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(community=self.request.community)
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
        )


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
            # .annotate(num_likes=Count("like"))
            .order_by("created")
        )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["comments"] = self.get_comments()
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data


class BaseActivityLikeView(
    ActivityQuerySetMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleObjectMixin,
    View,
):
    permission_required = "activities.like_activity"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Like.objects.create(user=request.user, activity=self.object)
        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())


class BaseActivityDislikeView(
    ActivityQuerySetMixin, LoginRequiredMixin, SingleObjectMixin, View
):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Like.objects.filter(user=request.user, activity=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityStreamView(BaseActivityListView):
    template_name = "activities/stream.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("-created")


activity_stream_view = ActivityStreamView.as_view()


class ActivitySearchView(BaseActivityListView):
    template_name = "activities/search.html"

    def get_queryset(self) -> QuerySet:
        self.search_query = self.request.GET.get("q", "").strip()
        if not self.search_query:
            return Activity.objects.none()

        return (
            super().get_queryset().search(self.search_query).order_by("-rank")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["search_query"] = self.search_query
        return data


activity_search_view = ActivitySearchView.as_view()


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
