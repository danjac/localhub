# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TemplateFormResponse, TurboFrame, TurboStream, redirect_303

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.comments.forms import CommentForm
from localhub.common.decorators import add_messages_to_response_header
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


@community_required
@login_required
@require_POST
def create_comment_view(request, pk, model):

    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk,)
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
    obj = get_object_or_404(
        get_activity_queryset(request, model, with_common_annotations=True), pk=pk,
    )
    return render_activity_detail(request, obj, template_name)


@community_required
@login_required
@require_POST
def activity_reshare_view(request, pk, model):
    obj = get_object_or_404(
        get_activity_queryset(request, model).unreshared(request.user), pk=pk
    )
    has_perm_or_403(request.user, "activities.reshare_activity", obj)
    reshare = obj.reshare(request.user)

    reshare.notify_on_publish()

    messages.success(
        request,
        _("You have reshared this %(model)s") % {"model": obj._meta.verbose_name},
    )
    return redirect(reshare)


@community_required
@login_required
@require_POST
def activity_publish_view(request, pk, model):
    obj = get_object_or_404(
        get_activity_queryset(request, model).filter(published__isnull=True), pk=pk
    )
    has_perm_or_403(request.user, "activities.change_activity", obj)

    obj.published = timezone.now()
    obj.save(update_fields=["published"])
    obj.notify_on_publish()

    messages.success(
        request,
        _("Your %(model)s has been published") % {"model": obj._meta.verbose_name},
    )

    return redirect(obj)


@community_required
@login_required
@require_POST
def activity_pin_view(request, pk, model, remove=False):

    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk)
    has_perm_or_403(request.user, "activities.pin_activity", obj)

    if remove:
        obj.is_pinned = False
    else:
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        obj.is_pinned = True

    obj.save()

    messages.success(
        request,
        "The %(model)s has been pinned to the top of the activity stream"
        % {"model": obj._meta.verbose_name},
    )

    return redirect(settings.HOME_PAGE_URL)


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def activity_bookmark_view(request, pk, model, remove=False):
    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk)
    has_perm_or_403(request.user, "activities.bookmark_activity", obj)

    if remove:
        obj.get_bookmarks().filter(user=request.user).delete()
        messages.info(request, _("You have removed this bookmark"))
    else:
        try:
            Bookmark.objects.create(
                user=request.user, community=request.community, content_object=obj,
            )
            messages.success(
                request,
                _("You have bookmarked this %(model)s")
                % {"model": obj._meta.verbose_name},
            )
        except IntegrityError:
            pass

    if request.accept_turbo_stream:
        return (
            TurboFrame(f"{obj.get_dom_id()}-bookmark")
            .template(
                "activities/includes/bookmark.html",
                {"object": obj, "has_bookmarked": not (remove)},
            )
            .response(request)
        )
    return redirect(obj)


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def activity_like_view(request, pk, model, remove=False):
    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk)
    has_perm_or_403(request.user, "activities.like_activity", obj)

    if remove:
        obj.get_likes().filter(user=request.user).delete()
        messages.info(
            request,
            _("You have stopped liking this %(model)s")
            % {"model": obj._meta.verbose_name},
        )
    else:

        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=obj.owner,
                content_object=obj,
            ).notify()

            messages.success(
                request,
                _("You have liked this %(model)s") % {"model": obj._meta.verbose_name},
            )

        except IntegrityError:
            pass

    if request.accept_turbo_stream:
        return (
            TurboFrame(f"{obj.get_dom_id()}-like")
            .template(
                "activities/includes/like.html",
                {"object": obj, "has_liked": not (remove)},
            )
            .response(request)
        )
    return redirect(obj)


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def activity_delete_view(request, pk, model):
    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk)
    has_perm_or_403(request.user, "activities.delete_activity", obj)

    if request.user != obj.owner:
        obj.soft_delete()
        obj.notify_on_delete(request.user)
    else:
        obj.delete()

    messages.success(
        request, _("%(model)s has been deleted") % {"model": obj._meta.verbose_name}
    )
    target = request.POST.get("target", None)

    if target:
        return TurboStream(target).remove.response()

    return redirect(
        settings.HOME_PAGE_URL if obj.deleted or obj.published else "activities:private"
    )


def get_activity_queryset(request, model, with_common_annotations=False):

    qs = (
        model.objects.for_community(request.community)
        .select_related("owner", "community", "parent", "parent__owner", "editor")
        .published_or_owner(request.user)
    )

    if with_common_annotations:
        qs = qs.with_common_annotations(request.user, request.community)
    return qs


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
    obj = get_object_or_404(get_activity_queryset(request, model), pk=pk,)
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


class BaseActivityListView(ActivityQuerySetMixin, ActivityTemplateMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE


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


class BaseActivityActionView(ActivityQuerySetMixin, ActionView):
    ...
