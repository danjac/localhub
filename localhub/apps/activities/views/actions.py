# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.bookmarks.models import Bookmark
from localhub.common.views import SuccessActionView, SuccessDeleteView
from localhub.likes.models import Like

from ..utils import get_activity_models
from .mixins import ActivityQuerySetMixin, ActivityTemplateMixin


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
    success_url = settings.LOCALHUB_HOME_PAGE_URL
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

    success_url = settings.LOCALHUB_HOME_PAGE_URL
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
