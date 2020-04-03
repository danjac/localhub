# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
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
from localhub.views import SearchMixin

from ..models import get_activity_models


class ActivityQuerySetMixin(CommunityRequiredMixin):
    model = None

    def get_queryset(self):
        return self.model._default_manager.for_community(
            self.request.community
        ).select_related("owner", "community", "parent", "parent__owner")


class BaseSingleActivityView(ActivityQuerySetMixin, GenericModelView):
    ...


class ActivityContextMixin:
    def get_context_data(self, **kwargs):
        return super().get_context_data(model=self.model, **kwargs)


class ActivityCreateView(
    CommunityRequiredMixin, PermissionRequiredMixin, ActivityContextMixin, CreateView,
):
    permission_required = "activities.create_activity"

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        message = (
            _("Your %(object)s has been published")
            if self.object.published
            else _("Your %(object)s has been saved to Drafts")
        )
        return message % {"object": self.object._meta.verbose_name}

    def form_valid(self, form):

        publish = "save_as_draft" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            self.object.notify_on_create()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityListView(
    ActivityQuerySetMixin, SearchMixin, ActivityContextMixin, ListView
):
    allow_empty = True
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE
    order_by = ("-published", "-created")

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .published()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked(self.request.user)
            .order_by(*self.order_by)
        )

        if self.search_query:
            qs = qs.search(self.search_query).order_by("-rank", *self.order_by)
        return qs


class ActivityUpdateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ActivityContextMixin, UpdateView,
):
    permission_required = "activities.change_activity"

    def get_success_message(self, publish):
        message = (
            _("Your %(activity)s has been published")
            if publish
            else _("Your %(activity)s has been updated")
        )
        return message % {"activity": self.object._meta.verbose_name}

    def form_valid(self, form):

        publish = (
            not (self.object.published) and "save_as_draft" not in self.request.POST
        )

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        if publish:
            self.object.published = timezone.now()
        self.object.save()
        self.object.update_reshares()

        if self.object.published:
            self.object.notify_on_update()

        messages.success(self.request, self.get_success_message(publish))
        return HttpResponseRedirect(self.get_success_url())


class ActivityDeleteView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ActivityContextMixin, DeleteView,
):
    permission_required = "activities.delete_activity"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    success_message = _("This %s has been deleted")

    def get_success_message(self):
        return self.success_message % self.object._meta.verbose_name

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class ActivityDetailView(ActivityQuerySetMixin, ActivityContextMixin, DetailView):
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

        data["comments"] = self.get_comments()
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


class ActivityReshareView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.reshare_activity"

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

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_success_message(self):

        return (
            _("You have reshared this %(object)s")
            % {"object": self.object._meta.verbose_name},
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.reshare = self.object.reshare(self.request.user)

        messages.success(self.request, self.get_success_message())

        self.reshare.notify_on_create()

        return HttpResponseRedirect(self.get_success_url())


class ActivityPublishView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.change_activity"

    def get_queryset(self):
        return super().get_queryset().filter(published__isnull=True)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.published = timezone.now()
        self.object.save(update_fields=["published"])
        message = (_("Your %(object)s has been published")) % {
            "object": self.object._meta.verbose_name
        }
        messages.success(request, message)
        return HttpResponseRedirect(self.get_success_url())


activity_publish_view = ActivityPublishView.as_view()


class ActivityPinView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.pin_activity"

    def get_success_url(self):
        return settings.LOCALHUB_HOME_PAGE_URL

    def get_success_message(self):
        return (
            _("The %(object)s has been pinned to the top of the activity stream")
            % {"object": self.object._meta.verbose_name},
        )

    def post(self, request, *args, **kwargs):
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        self.object = self.get_object()
        self.object.is_pinned = True
        self.object.save()

        messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityUnpinView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.pin_activity"

    def get_success_url(self):
        return settings.LOCALHUB_HOME_PAGE_URL

    def get_success_message(self):
        return (
            _("The %(object)s has been removed from the top of the activity stream")
            % {"object": self.object._meta.verbose_name},
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_pinned = False
        self.object.save()
        messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityBookmarkView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.bookmark_activity"

    def get_success_url(self):
        return self.object.get_absolute_url()

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
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponse(self.get_success_url())


class ActivityRemoveBookmarkView(BaseSingleActivityView):
    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.get_bookmarks().filter(user=request.user).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponse(self.get_success_url())

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityLikeView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.like_activity"

    def get_success_url(self):
        return self.object.get_absolute_url()

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
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponse(self.get_success_url())


class ActivityDislikeView(BaseSingleActivityView):
    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.get_likes().filter(user=request.user).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponse(self.get_success_url())

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, FormView,
):
    form_class = FlagForm
    template_name = "activities/flag_form.html"
    permission_required = "activities.flag_activity"

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
        return self.activity.get_absolute_url()

    def get_success_message(self):

        return (
            _(
                "This %(activity)s has been flagged to the moderators"
                % {"activity": self.activity._meta.verbose_name}
            ),
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.activity
        self.object.community = self.request.community
        self.object.user = self.request.user
        self.object.save()

        self.object.notify()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


activity_flag_view = ActivityFlagView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, FormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"

    @cached_property
    def activity(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_permission_object(self):
        return self.activity

    def get_success_url(self):
        return self.activity.get_absolute_url()

    def get_success_message(self):
        return _("Your comment has been posted")

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.content_object = self.activity
        comment.community = self.request.community
        comment.owner = self.request.user
        comment.save()

        comment.notify_on_create()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            activity=self.activity, activity_model=self.activity.__class__, **kwargs
        )
