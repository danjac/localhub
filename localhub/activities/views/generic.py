# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    GenericModelView,
    ListView,
    UpdateView,
)

from localhub.bookmarks.models import Bookmark
from localhub.comments.forms import CommentForm
from localhub.communities.views import CommunityRequiredMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like
from localhub.pagination import PresetCountPaginator
from localhub.views import SearchMixin, SuccessMixin

from ..models import get_activity_models


class ActivityQuerySetMixin(CommunityRequiredMixin):
    model = None

    def get_queryset(self):
        return self.model._default_manager.for_community(
            self.request.community
        ).select_related("owner", "community", "parent", "parent__owner")


class BaseSingleActivityView(ActivityQuerySetMixin, GenericModelView):
    ...


class ActivityTemplateMixin:
    """Includes extra template name option of "activities/activity_{suffix}.html"
    """

    def get_template_names(self):
        return super().get_template_names() + [
            f"activities/activity{self.template_name_suffix}.html"
        ]


class ActivityCreateView(
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    ActivityTemplateMixin,
    SuccessMixin,
    CreateView,
):
    permission_required = "activities.create_activity"

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return super().get_success_message(
            _("Your %(model)s has been published")
            if self.object.published
            else _("Your %(model)s has been saved to your Private Stash")
        )

    def form_valid(self, form):

        publish = "save_private" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            self.object.notify_on_create()

        return self.success_response()


class ActivityListView(
    ActivityQuerySetMixin, ActivityTemplateMixin, SearchMixin, ListView
):
    allow_empty = True
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE
    ordering = "-published"

    def get_ordering(self):
        if isinstance(self.ordering, str):
            ordering = [self.ordering]
        else:
            ordering = list(self.ordering)

        if self.search_query:
            ordering = ["-rank"] + ordering

        return ordering

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .published()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked(self.request.user)
        )

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs.order_by(*self.get_ordering())


class ActivityUpdateView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been updated")

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.update_reshares()

        if self.object.published:
            self.object.notify_on_update()

        return self.success_response()


class ActivityDeleteView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessMixin,
    DeleteView,
):
    permission_required = "activities.delete_activity"
    success_message = _("This %(model)s has been deleted")

    def get_success_url(self):
        if self.object.deleted or self.object.published:
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("activities:private")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()


class ActivityDetailView(ActivityQuerySetMixin, ActivityTemplateMixin, DetailView):
    paginator_class = PresetCountPaginator
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE
    page_kwarg = "page"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()

        data["comments"] = self.get_comments_page(self.get_comments())
        if self.request.user.has_perm("activities.create_comment", self.object):
            data["comment_form"] = CommentForm()

        data["reshares"] = self.get_reshares()
        return data

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("editor")
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
        )

    def get_flags(self):
        return self.object.get_flags().select_related("user").order_by("-created")

    def get_reshares(self):
        return (
            self.object.reshares.for_community(self.request.community)
            .exclude_blocked_users(self.request.user)
            .select_related("owner")
            .order_by("-created")
        )

    def get_comments(self):
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.user, self.request.community)
            .for_community(self.request.community)
            .exclude_deleted()
            .select_related(
                "owner", "community", "parent", "parent__owner", "parent__community",
            )
            .order_by("created")
        )

    def get_comments_page(self, comments):
        return self.paginator_class(
            object_list=comments,
            count=self.object.num_comments or 0,
            per_page=self.paginate_by,
            allow_empty_first_page=True,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))


class ActivityReshareView(
    PermissionRequiredMixin, SuccessMixin, BaseSingleActivityView
):
    permission_required = "activities.reshare_activity"
    success_message = _("You have reshared this %(model)s")

    def get_queryset(self):
        """
        Make sure user has only reshared once.
        """
        return (
            super()
            .get_queryset()
            .with_has_reshared(self.request.user)
            .filter(has_reshared=False)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.reshare = self.object.reshare(self.request.user)

        self.reshare.notify_on_create()

        return self.success_response()


class ActivityPublishView(
    PermissionRequiredMixin, SuccessMixin, BaseSingleActivityView
):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been published")

    def get_queryset(self):
        return super().get_queryset().filter(published__isnull=True)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.published = timezone.now()
        self.object.save(update_fields=["published"])

        return self.success_response()


activity_publish_view = ActivityPublishView.as_view()


class ActivityPinView(PermissionRequiredMixin, SuccessMixin, BaseSingleActivityView):
    permission_required = "activities.pin_activity"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been pinned to the top of the activity stream"
    )

    def post(self, request, *args, **kwargs):
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        self.object = self.get_object()
        self.object.is_pinned = True
        self.object.save()

        return self.success_response()


class ActivityUnpinView(PermissionRequiredMixin, SuccessMixin, BaseSingleActivityView):
    permission_required = "activities.pin_activity"

    success_url = settings.LOCALHUB_HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been unpinned from the top of the activity stream"
    )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_pinned = False
        self.object.save()

        return self.success_response()


class BaseActivityBookmarkView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.bookmark_activity"
    template_name = "activities/includes/bookmark.html"

    def success_response(self, has_bookmarked):
        return self.render_to_response(
            {
                "object": self.object,
                "object_type": self.object._meta.model_name,
                "has_bookmarked": has_bookmarked,
            }
        )


class ActivityBookmarkView(BaseActivityBookmarkView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            # dupe, ignore
            pass
        return self.success_response(has_bookmarked=True)


class ActivityRemoveBookmarkView(BaseActivityBookmarkView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.get_bookmarks().filter(user=request.user).delete()
        return self.success_response(has_bookmarked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class BaseActivityLikeView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.like_activity"
    template_name = "activities/includes/like.html"

    def success_response(self, has_liked):
        return self.render_to_response(
            {
                "object": self.object,
                "object_type": self.object._meta.model_name,
                "has_liked": has_liked,
            }
        )


class ActivityLikeView(BaseActivityLikeView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            ).notify()

        except IntegrityError:
            # dupe, ignore
            pass
        return self.success_response(has_liked=True)


class ActivityDislikeView(BaseActivityLikeView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.get_likes().filter(user=request.user).delete()
        return self.success_response(has_liked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, SuccessMixin, FormView,
):
    form_class = FlagForm
    template_name = "activities/flag_form.html"
    permission_required = "activities.flag_activity"
    success_message = _("This %(model)s has been flagged to the moderators")

    @cached_property
    def activity(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            activity=self.activity, activity_model=self.activity.__class__, **kwargs
        )

    def get_permission_object(self):
        return self.activity

    def get_success_url(self):
        return super().get_success_url(object=self.activity)

    def get_success_message(self):
        return super().get_success_message(model=self.activity)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.activity
        self.object.community = self.request.community
        self.object.user = self.request.user
        self.object.save()

        self.object.notify()

        return self.success_response()


activity_flag_view = ActivityFlagView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, SuccessMixin, FormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"
    success_message = _("Your %(model)s has been posted")

    @cached_property
    def activity(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_permission_object(self):
        return self.activity

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.activity
        self.object.community = self.request.community
        self.object.owner = self.request.user
        self.object.save()

        self.object.notify_on_create()

        return self.success_response()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            activity=self.activity, activity_model=self.activity.__class__, **kwargs
        )
