# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import TurboFrame, TurboStream, redirect_303, render_form_response

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.comments.forms import CommentForm
from localhub.common.decorators import add_messages_to_response_header
from localhub.common.forms import process_form
from localhub.common.pagination import get_pagination_context, render_paginated_queryset
from localhub.common.template.defaultfilters import resolve_url
from localhub.communities.decorators import community_required
from localhub.flags.views import handle_flag_create
from localhub.likes.models import Like
from localhub.users.utils import has_perm_or_403

# Local
from ..forms import ActivityTagsForm
from ..utils import get_activity_models


@community_required
@login_required
def activity_create_view(
    request, model, form_class, template_name, is_private=False, extra_context=None,
):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    return handle_activity_create(
        request,
        model,
        form_class,
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
    obj = get_activity_or_404(
        request,
        get_activity_queryset(request, model, with_common_annotations=True),
        pk=pk,
    )
    return render_activity_detail(request, obj, template_name)


@community_required
@login_required
@require_POST
def activity_reshare_view(request, pk, model):
    obj = get_activity_or_404(
        request,
        get_activity_queryset(request, model).unreshared(request.user),
        pk,
        permission="activities.reshare_activity",
    )

    reshare = obj.reshare(request.user)

    reshare.notify_on_publish()

    messages.success(
        request, model_translation_string(_("You have reshared this %(model)s"), obj)
    )
    return redirect(reshare)


@community_required
@login_required
@require_POST
def activity_publish_view(request, pk, model):
    obj = get_activity_or_404(
        request,
        get_activity_queryset(request, model).filter(published__isnull=True),
        pk,
        permission="activities.change_activity",
    )

    obj.published = timezone.now()
    obj.save(update_fields=["published"])
    obj.notify_on_publish()

    messages.success(
        request, model_translation_string(_("Your %(model)s has been published"), obj)
    )

    return redirect(obj)


@community_required
@login_required
@require_POST
def activity_pin_view(request, pk, model, remove=False):

    obj = get_activity_or_404(request, model, pk, permission="activities.pin_activity")

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
        model_translation_string(
            _("The %(model)s has been pinned to the top of the activity stream"), obj
        ),
    )

    return redirect(settings.HOME_PAGE_URL)


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def activity_bookmark_view(request, pk, model, remove=False):
    obj = get_activity_or_404(
        request, model, pk, permission="activities.bookmark_activity"
    )

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
                model_translation_string(_("You have bookmarked this %(model)s"), obj),
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
    obj = get_activity_or_404(request, model, pk, permission="activities.like_activity")

    if remove:
        obj.get_likes().filter(user=request.user).delete()
        messages.info(
            request,
            model_translation_string(_("You have stopped liking this %(model)s"), obj),
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
                model_translation_string(_("You have liked this %(model)s"), obj),
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
    obj = get_activity_or_404(
        request, model, pk, permission="activities.delete_activity"
    )

    if request.user != obj.owner:
        obj.soft_delete()
        obj.notify_on_delete(request.user)
    else:
        obj.delete()

    messages.success(
        request, model_translation_string(_("%(model)s has been deleted"), obj)
    )
    target = request.POST.get("target", None)

    if target:
        return TurboStream(target).remove.response()

    return redirect(
        settings.HOME_PAGE_URL if obj.deleted or obj.published else "activities:private"
    )


@community_required
@login_required
def activity_flag_view(request, pk, model):
    obj = get_activity_or_404(
        request,
        get_activity_queryset(request, model)
        .with_has_flagged(request.user)
        .exclude(has_flagged=True),
        pk,
        permission="activities.flag_activity",
    )

    return handle_flag_create(request, obj)


def get_activity_queryset(request, model, with_common_annotations=False):

    qs = (
        model.objects.for_community(request.community)
        .select_related("owner", "community", "parent", "parent__owner", "editor")
        .published_or_owner(request.user)
    )

    if with_common_annotations:
        qs = qs.with_common_annotations(request.user, request.community)
    return qs


def get_activity_or_404(request, model_or_queryset, pk, *, permission=None):

    queryset = (
        model_or_queryset
        if isinstance(model_or_queryset, QuerySet)
        else get_activity_queryset(request, model_or_queryset)
    )

    obj = get_object_or_404(queryset, pk=pk)

    if permission:
        has_perm_or_403(request.user, permission, obj)
    return obj


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

    return render_paginated_queryset(
        request,
        queryset,
        template_name,
        {"model": queryset.model, **(extra_context or {}),},
    )


def handle_activity_create(
    request,
    model,
    form_class,
    template_name,
    *,
    is_private=False,
    extra_context=None,
    **form_kwargs,
):
    obj, form, success = process_activity_create_form(
        request, model, form_class, is_private=is_private, **form_kwargs
    )

    if success:
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
    **form_kwargs,
):
    obj = get_activity_or_404(request, model, pk, permission=permission)
    obj, form, success = process_activity_update_form(
        request, form_class, instance=obj, **form_kwargs
    )
    if success:
        return redirect_303(obj)

    return render_activity_update_form(
        request, obj, form, template_name, extra_context=extra_context,
    )


def process_activity_create_form(
    request, model, form_class, *, is_private=False, **form_kwargs
):

    with process_form(request, form_class, **form_kwargs) as (form, success):
        if success:

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
            )

            messages.success(request, model_translation_string(success_message, obj))

            return obj, form, True

    return None, form, False


def process_activity_update_form(request, form_class, instance, **form_kwargs):

    with process_form(request, form_class, instance=instance, **form_kwargs) as (
        form,
        success,
    ):

        if success:
            instance = form.save(commit=False)
            instance.editor = request.user
            instance.edited = timezone.now()
            instance.save()

            instance.update_reshares()

            if instance.published:
                instance.notify_on_update()

            success_message = model_translation_string(
                _("Your %(model)s has been updated"), instance
            )

            messages.success(request, success_message)

            return instance, form, True
    return instance, form, False


def render_activity_create_form(
    request, model, form, template_name, *, is_private=False, extra_context=None
):

    view_name = "create_private" if is_private else "create"

    submit_actions = [
        (
            resolve_url(activity_model, view_name),
            model_translation_string(
                _("Submit %(model)s"), activity_model, capitalize=True
            ),
        )
        for activity_model in get_activity_models()
        if activity_model != model
    ]

    return render_form_response(
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

    return render_form_response(
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
        "reshares": reshares,
        **get_pagination_context(request, comments),
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


def model_translation_string(value, model, capitalize=False):
    model_name = model._meta.verbose_name
    if capitalize:
        model_name = model_name.capitalize()
    return value % {"model": model_name}
