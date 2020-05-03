# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from rules.contrib.views import PermissionRequiredMixin

from social_bfg.apps.bookmarks.models import Bookmark
from social_bfg.apps.comments.forms import CommentForm
from social_bfg.apps.communities.views import CommunityRequiredMixin
from social_bfg.apps.flags.forms import FlagForm
from social_bfg.apps.likes.models import Like
from social_bfg.pagination import PresetCountPaginator
from social_bfg.template.defaultfilters import resolve_url
from social_bfg.views import (
    ParentObjectMixin,
    SearchMixin,
    SuccessActionView,
    SuccessCreateView,
    SuccessDeleteView,
    SuccessFormView,
    SuccessUpdateView,
)

from ..forms import ActivityTagsForm
from ..utils import get_activity_models


class ActivityQuerySetMixin(CommunityRequiredMixin):
    model = None

    def get_queryset(self):
        return self.model._default_manager.for_community(
            self.request.community
        ).select_related("owner", "community", "parent", "parent__owner")


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
    SuccessCreateView,
):
    permission_required = "activities.create_activity"

    is_private = False
    is_new = True

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return super().get_success_message(
            _("Your %(model)s has been published")
            if self.object.published
            else _("Your %(model)s has been saved to your Private Stash")
        )

    def get_submit_actions(self):
        view_name = "create_private" if self.is_private else "create"
        return [
            (
                resolve_url(model, view_name),
                _("Submit %(model)s")
                % {"model": model._meta.verbose_name.capitalize()},
            )
            for model in get_activity_models()
            if model != self.model
        ]

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["submit_actions"] = self.get_submit_actions()
        return data

    def form_valid(self, form):

        publish = self.is_private is False and "save_private" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            self.object.notify_on_publish()

        return self.success_response()


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ParentObjectMixin, SuccessFormView,
):
    form_class = FlagForm
    template_name = "activities/flag_form.html"
    permission_required = "activities.flag_activity"
    success_message = _("This %(model)s has been flagged to the moderators")

    parent_object_name = "activity"

    def get_parent_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
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
    PermissionRequiredMixin, ActivityQuerySetMixin, ParentObjectMixin, SuccessFormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"
    success_message = _("Your %(model)s has been posted")

    parent_object_name = "content_object"

    def get_permission_object(self):
        return self.content_object

    def get_parent_queryset(self):
        return self.get_queryset()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.content_object
        self.object.community = self.request.community
        self.object.owner = self.request.user
        self.object.save()

        self.object.notify_on_create()

        return self.success_response()


class ActivityUpdateView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessUpdateView,
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


class ActivityUpdateTagsView(ActivityUpdateView):
    """
    Allows a moderator to update the tags on a view, e.g
    to add a "content sensitive" tag.
    """

    form_class = ActivityTagsForm
    permission_required = "activities.change_activity_tags"
    success_message = _("Tags have been updated")

    def get_queryset(self):
        return super().get_queryset().published()


class BaseActivityListView(ActivityQuerySetMixin, ActivityTemplateMixin, ListView):
    allow_empty = True
    paginate_by = settings.SOCIAL_BFG_DEFAULT_PAGE_SIZE


class ActivityListView(SearchMixin, BaseActivityListView):
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


class ActivityDetailView(ActivityQuerySetMixin, ActivityTemplateMixin, DetailView):
    paginator_class = PresetCountPaginator
    paginate_by = settings.SOCIAL_BFG_DEFAULT_PAGE_SIZE
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
        return (
            self.object.get_flags()
            .select_related("user")
            .prefetch_related("content_object")
            .order_by("-created")
        )

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
            .with_common_related()
            .order_by("created")
        )

    def get_comments_page(self, comments):
        return self.paginator_class(
            object_list=comments,
            count=self.object.num_comments or 0,
            per_page=self.paginate_by,
            allow_empty_first_page=True,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))


class BaseActivityActionView(
    ActivityQuerySetMixin, PermissionRequiredMixin, SuccessActionView
):
    ...


class ActivityReshareView(BaseActivityActionView):
    permission_required = "activities.reshare_activity"
    success_message = _("You have reshared this %(model)s")

    def get_queryset(self):
        """
        Make sure user has only reshared once.
        """
        return super().get_queryset().unreshared(self.request.user)

    def get_success_url(self):
        return self.reshare.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.reshare = self.object.reshare(self.request.user)

        self.reshare.notify_on_publish()

        return self.success_response()


class ActivityPublishView(BaseActivityActionView):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been published")

    def get_queryset(self):
        return super().get_queryset().filter(published__isnull=True)

    def post(self, request, *args, **kwargs):
        self.object.published = timezone.now()
        self.object.save(update_fields=["published"])
        self.object.notify_on_publish()

        return self.success_response()


activity_publish_view = ActivityPublishView.as_view()


class ActivityPinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"
    success_url = settings.SOCIAL_BFG_HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been pinned to the top of the activity stream"
    )

    def post(self, request, *args, **kwargs):
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        self.object.is_pinned = True
        self.object.save()

        return self.success_response()


class ActivityUnpinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"

    success_url = settings.SOCIAL_BFG_HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been unpinned from the top of the activity stream"
    )

    def post(self, request, *args, **kwargs):
        self.object.is_pinned = False
        self.object.save()

        return self.success_response()


class BaseActivityBookmarkView(BaseActivityActionView):
    permission_required = "activities.bookmark_activity"
    is_success_ajax_response = True


class ActivityBookmarkView(BaseActivityBookmarkView):
    success_message = _("You have added this %(model)s to your bookmarks")

    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            # dupe, ignore
            pass
        return self.success_response()


class ActivityRemoveBookmarkView(BaseActivityBookmarkView):
    success_message = _("You have removed this %(model)s from your bookmarks")

    def post(self, request, *args, **kwargs):
        self.object.get_bookmarks().filter(user=request.user).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class BaseActivityLikeView(BaseActivityActionView):
    permission_required = "activities.like_activity"
    is_success_ajax_response = True


class ActivityLikeView(BaseActivityLikeView):
    success_message = _("You have liked this %(model)s")

    def post(self, request, *args, **kwargs):
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
        return self.success_response()


class ActivityDislikeView(BaseActivityLikeView):
    success_message = _("You have stopped liking this %(model)s")

    def post(self, request, *args, **kwargs):
        self.object.get_likes().filter(user=request.user).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityDeleteView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessDeleteView,
):
    permission_required = "activities.delete_activity"
    success_message = _("You have deleted this %(model)s")

    def get_success_url(self):
        if self.object.deleted or self.object.published:
            return settings.SOCIAL_BFG_HOME_PAGE_URL
        return reverse("activities:private")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()
