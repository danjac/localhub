# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TemplateFormResponse, TurboFrame, TurboStream, redirect_303

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.comments.forms import CommentForm
from localhub.common.mixins import SuccessHeaderMixin
from localhub.common.template.defaultfilters import resolve_url
from localhub.common.views import ActionView
from localhub.communities.decorators import community_required
from localhub.flags.views import BaseFlagCreateView
from localhub.likes.models import Like
from localhub.users.utils import has_perm_or_403

# Local
from ..forms import ActivityTagsForm
from ..mixins import ActivityQuerySetMixin, ActivityTemplateMixin
from ..utils import get_activity_models


@community_required
@login_required
def activity_create_view(
    request, model, form_class, template_name, is_private=False, extra_context=None,
):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
    else:
        form = form_class()

    return handle_activity_create(
        request,
        model,
        form,
        template_name,
        is_private=is_private,
        extra_context=extra_context,
    )


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, BaseFlagCreateView
):
    permission_required = "activities.flag_activity"
    success_message = _("This %(model)s has been flagged to the moderators")

    def get_parent_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.parent


activity_flag_view = ActivityFlagView.as_view()


@community_required
@login_required
@require_POST
def create_comment_view(request, pk, model):

    obj = get_object_or_404(
        model.objects.for_community(request.community).select_related(
            "owner", "community"
        ),
        pk=pk,
    )
    has_perm_or_403(request.user, "activities.create_comment", obj)

    form = CommentForm(request.POST)
    if form.is_valid():

        comment = form.save(commit=False)
        comment.content_object = obj
        comment.community = request.community
        comment.owner = request.user
        comment.save()

        comment.notify_on_create()

        messages.success(request, _("Your comment has been posted"))

        return redirect(obj)

    return (
        TurboStream("comment-form")
        .replace.template(
            "activities/includes/comment_form.html", {"form": form, "object": obj}
        )
        .response(request)
    )


@community_required
@login_required
def activity_update_view(request, pk, model, form_class, template_name):
    return handle_activity_update(request, pk, model, form_class, template_name)


@community_required
@login_required
def activity_update_tags_view(request, pk, model, template_name):
    return handle_activity_update(
        request,
        pk,
        model,
        form_class=ActivityTagsForm,
        template_name=template_name,
        permission="activities.change_activity_tags",
    )


@community_required
def activity_list_view(
    request,
    model,
    template_name,
    ordering=("-created", "-published"),
    extra_context=None,
):
    return render_activity_list(
        request,
        get_activity_queryset(request, model),
        template_name,
        ordering,
        extra_context,
    )


@community_required
def activity_detail_view(request, pk, model, template_name, slug=None):
    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk,)
    return render_activity_detail(request, obj, template_name)


def render_activity_detail(request, obj, template_name, *, extra_context=None):

    if request.user.is_authenticated:
        obj.get_notifications().for_recipient(request.user).unread().update(
            is_read=True
        )

    comments = (
        obj.get_comments()
        .for_community(request.community)
        .with_common_annotations(request.user, request.community)
        .exclude_deleted()
        .with_common_related()
        .order_by("created")
    )

    reshares = (
        obj.reshares.for_community(request.community)
        .exclude_blocked_users(request.user)
        .select_related("owner")
        .order_by("-created")
    )

    context = {
        "object": obj,
        "comments": comments,
        "reshares": reshares,
    }

    if request.user.has_perm("communities.moderate_community", request.community):
        context["flags"] = (
            obj.get_flags()
            .select_related("user")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    if request.user.has_perm("activities.create_comment", obj):
        context["comment_form"] = CommentForm()

    return TemplateResponse(
        request, template_name, {**context, **(extra_context or {})}
    )


class BaseActivityActionView(ActivityQuerySetMixin, ActionView):
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

        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )

        return self.render_to_response()


class ActivityPublishView(SuccessHeaderMixin, BaseActivityActionView):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been published")

    def get_queryset(self):
        return super().get_queryset().filter(published__isnull=True)

    def post(self, request, *args, **kwargs):
        self.object.published = timezone.now()
        self.object.save(update_fields=["published"])
        self.object.notify_on_publish()
        return self.render_success_message(self.render_to_response())


activity_publish_view = ActivityPublishView.as_view()


class ActivityPinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been pinned to the top of the activity stream"
    )

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        self.object.is_pinned = True
        self.object.save()

        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )
        return self.render_to_response()


class ActivityUnpinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been unpinned from the top of the activity stream"
    )

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        self.object.is_pinned = False
        self.object.save()
        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )
        return self.render_to_response()


class BaseActivityBookmarkView(BaseActivityActionView):
    permission_required = "activities.bookmark_activity"

    def render_to_response(self, has_bookmarked):
        return (
            TurboFrame(self.object.get_dom_id() + "-bookmark")
            .template(
                "activities/includes/bookmark.html",
                {"object": self.object, "has_bookmarked": has_bookmarked},
            )
            .response(self.request)
        )


class ActivityBookmarkView(BaseActivityBookmarkView):
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
        return self.render_to_response(has_bookmarked=True)


class ActivityRemoveBookmarkView(BaseActivityBookmarkView):
    def post(self, request, *args, **kwargs):
        self.object.get_bookmarks().filter(user=request.user).delete()
        return self.render_to_response(has_bookmarked=False)


class BaseActivityLikeView(BaseActivityActionView):
    permission_required = "activities.like_activity"

    def render_to_response(self, has_liked):
        return (
            TurboFrame(self.object.get_dom_id() + "-like")
            .template(
                "activities/includes/like.html",
                {"object": self.object, "has_liked": has_liked},
            )
            .response(self.request)
        )


class ActivityLikeView(BaseActivityLikeView):
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
        return self.render_to_response(has_liked=True)


class ActivityDislikeView(BaseActivityLikeView):
    def post(self, request, *args, **kwargs):
        self.object.get_likes().filter(user=request.user).delete()
        return self.render_to_response(has_liked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityDeleteView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessHeaderMixin,
    DeleteView,
):
    permission_required = "activities.delete_activity"
    success_message = _("You have deleted this %(model)s")

    def get_success_url(self):
        if self.object.deleted or self.object.published:
            return settings.HOME_PAGE_URL
        return reverse("activities:private")

    def get_success_message(self):
        return self.success_message % {"model": self.object._meta.verbose_name}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        target = request.POST.get("target", None)
        if target:
            return self.render_success_message(TurboStream(target).remove.response())

        messages.success(request, self.get_success_message())

        return HttpResponseRedirect(self.get_success_url())


def get_activity_queryset(request, model):
    return (
        model.objects.for_community(request.community)
        .select_related("owner", "community", "parent", "parent__owner", "editor")
        .published_or_owner(request.user)
        .with_common_annotations(request.user, request.community)
    )


def render_activity_list(
    request,
    queryset,
    template_name,
    ordering=("-created", "-published"),
    extra_context=None,
):

    if search := request.GET.get("q"):
        queryset = queryset.search(search)

    if isinstance(ordering, str):
        ordering = [ordering]
    else:
        ordering = list(ordering)
    if search:
        ordering = ["-rank"] + ordering

    queryset = queryset.order_by(*ordering)

    return TemplateResponse(
        request,
        template_name,
        {"object_list": queryset, "model": queryset.model, **(extra_context or {})},
    )


def handle_activity_create(
    request, model, form, template_name, *, is_private=False, extra_context=None,
):
    obj, ok = process_activity_create_form(request, model, form, is_private=is_private)

    if ok:
        return redirect_303(obj)

    return render_activity_create_form(
        request,
        model,
        form,
        template_name,
        is_private=is_private,
        extra_context=extra_context,
    )


def handle_activity_update(
    request,
    pk,
    model,
    form_class,
    template_name,
    *,
    permission="activities.change_activity",
    extra_context=None,
):
    obj = get_activity_for_update(request, model, pk, permission)
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=obj)
    else:
        form = form_class(instance=obj)
    obj, ok = process_activity_update_form(request, obj, form)
    if ok:
        return redirect_303(obj)

    return render_activity_update_form(
        request, obj, form, template_name, extra_context=extra_context,
    )


def get_activity_for_update(
    request, model, pk, permission="activities.change_activity"
):
    obj = get_object_or_404(
        model.objects.for_community(request.community).select_related(
            "owner", "community"
        ),
        pk=pk,
    )
    has_perm_or_403(request.user, permission, obj)
    return obj


def process_activity_create_form(request, model, form, *, is_private=False):

    if request.method == "POST" and form.is_valid():

        publish = is_private is False and "save_private" not in request.POST

        obj = form.save(commit=False)
        obj.owner = request.user
        obj.community = request.community

        if publish:
            obj.published = timezone.now()

        obj.save()

        if publish:
            obj.notify_on_publish()

        success_message = (
            _("Your %(model)s has been published")
            if obj.published
            else _("Your %(model)s has been saved to your Private Stash")
        ) % {"model": model._meta.verbose_name}

        messages.success(request, success_message)

        return obj, True

    return None, False


def process_activity_update_form(request, obj, form):

    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.editor = request.user
        obj.edited = timezone.now()
        obj.save()

        obj.update_reshares()

        if obj.published:
            obj.notify_on_update()

        success_message = _("Your %(model)s has been updated") % {
            "model": obj._meta.verbose_name
        }

        messages.success(request, success_message)

        return obj, True
    return obj, False


def render_activity_create_form(
    request, model, form, template_name, *, is_private=False, extra_context=None
):

    view_name = "create_private" if is_private else "create"

    submit_actions = [
        (
            resolve_url(activity_model, view_name),
            _("Submit %(model)s")
            % {"model": activity_model._meta.verbose_name.capitalize()},
        )
        for activity_model in get_activity_models()
        if activity_model != model
    ]

    return TemplateFormResponse(
        request,
        form,
        template_name,
        {
            "model": model,
            "is_private": is_private,
            "is_new": True,
            "submit_actions": submit_actions,
            **(extra_context or {}),
        },
    )


def render_activity_update_form(
    request, obj, form, template_name, *, extra_context=None
):

    return TemplateFormResponse(
        request,
        form,
        template_name,
        {"object": obj, "model": obj, "is_new": False, **(extra_context or {}),},
    )


class BaseActivityListView(ActivityQuerySetMixin, ActivityTemplateMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
