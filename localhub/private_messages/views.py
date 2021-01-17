# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import TemplateFormResponse, TurboFrame, TurboStream, redirect_303

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.common.decorators import add_messages_to_response_header
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_required
from localhub.users.utils import has_perm_or_403

# Local
from .forms import MessageForm, MessageRecipientForm
from .models import Message


@community_required
@login_required
def message_reply_view(request, pk, is_follow_up=False):

    has_perm_or_403(request.user, "private_messages.create_message", request.community)

    qs = (
        Message.objects.for_community(request.community)
        .exclude_blocked(request.user)
        .common_select_related()
    )

    if is_follow_up:
        qs = qs.for_sender(request.user)
    else:
        qs = qs.for_recipient(request.user)

    parent = get_object_or_404(qs, pk=pk)
    recipient = parent.get_other_user(request.user)

    form = MessageForm(request.POST if request.method == "POST" else None)

    form["message"].label = (
        _("Send follow-up to %(recipient)s")
        if is_follow_up
        else _("Send reply to %(recipient)s")
    ) % {"recipient": recipient.get_display_name()}

    if request.method == "POST" and form.is_valid():

        message = form.save(commit=False)
        message.community = request.community
        message.sender = request.user
        message.recipient = recipient
        message.parent = parent
        message.save()

        message.notify_on_reply()

        messages.success(
            request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": recipient.get_display_name()},
        )

        return redirect_303(message)

    return TemplateFormResponse(
        request,
        form,
        "private_messages/message_form.html",
        {"recipient": recipient, "parent": parent},
    )


@community_required
@login_required
@add_messages_to_response_header
def message_recipient_create_view(request, username):

    has_perm_or_403(request.user, "private_messages.create_message", request.community)

    recipient = get_object_or_404(
        get_user_model()
        .objects.exclude(pk=request.user.id)
        .for_community(request.community)
        .exclude_blocking(request.user),
        username__iexact=username,
    )

    form = MessageForm(request.POST if request.method == "POST" else None)

    form["message"].label = _(
        "Send message to %(recipient)s" % {"recipient": recipient.get_display_name()}
    )

    frame = TurboFrame("modal")

    if request.method == "POST" and form.is_valid():

        message = form.save(commit=False)
        message.community = request.community
        message.sender = request.user
        message.recipient = recipient
        message.save()

        message.notify_on_send()

        messages.success(
            request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": recipient.get_display_name()},
        )

        return frame.response()

    return frame.template(
        "private_messages/includes/modal_message_form.html",
        {"form": form, "recipient": recipient},
    ).response(request)


@community_required
@login_required
def message_create_view(request):

    form = MessageRecipientForm(
        request.POST if request.method == "POST" else None,
        community=request.community,
        sender=request.user,
    )

    if request.method == "POST" and form.is_valid():
        message = form.save(commit=False)
        message.community = request.community
        message.sender = request.user
        message.save()
        message.notify_on_send()

        messages.success(
            request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": message.recipient.get_display_name()},
        )

        return redirect_303(message)

    return TemplateFormResponse(request, form, "private_messages/message_form.html",)


@community_required
@login_required
def inbox_view(request):
    messages = (
        Message.objects.for_community(community=request.community)
        .with_has_bookmarked(request.user)
        .for_recipient(request.user)
        .exclude_blocked(request.user)
        .common_select_related()
    )
    if search := request.GET.get("q"):
        messages = messages.search(search).order_by("-rank", "-created")
    else:
        messages = messages.order_by(F("read").desc(nulls_first=True), "-created")

    return render_paginated_queryset(
        request, messages, "private_messages/inbox.html", {"search": search},
    )


@community_required
@login_required
def outbox_view(request):
    messages = (
        Message.objects.for_community(community=request.community)
        .with_has_bookmarked(request.user)
        .for_sender(request.user)
        .exclude_blocked(request.user)
        .common_select_related()
    )
    if search := request.GET.get("q"):
        messages = messages.search(search).order_by("-rank", "-created")
    else:
        messages = messages.order_by("-created")

    return render_paginated_queryset(
        request, messages, "private_messages/outbox.html", {"search": search},
    )


@community_required
@login_required
def message_detail_view(request, pk):
    message = get_object_or_404(
        Message.objects.for_community(request.community)
        .for_sender_or_recipient(request.user)
        .exclude_blocked(request.user)
        .with_has_bookmarked(request.user)
        .common_select_related(),
        pk=pk,
    )

    if message.recipient == request.user:
        message.mark_read(mark_replies=True)

    return TemplateResponse(
        request,
        "private_messages/message_detail.html",
        {
            "message": message,
            "parent": message.get_parent(request.user),
            "other_user": message.get_other_user(request.user),
            "replies": (
                message.get_all_replies()
                .for_sender_or_recipient(request.user)
                .common_select_related()
                .order_by("created")
                .distinct()
            ),
        },
    )


@community_required
@login_required
def message_mark_all_read_view(request):
    Message.objects.for_community(request.community).for_recipient(
        request.user
    ).unread().mark_read()
    return redirect("private_messages:inbox")


@community_required
@login_required
def message_mark_read_view(request, pk):

    message = get_object_or_404(
        Message.objects.for_community(request.community)
        .for_recipient(request.user)
        .unread(),
        pk=pk,
    )
    message.mark_read()

    return TurboStream(f"message-{message.id}-mark-read").remove.response()


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def message_bookmark_view(request, pk, remove=False):
    message = get_object_or_404(
        Message.objects.for_community(request.community).for_sender_or_recipient(
            request.user
        ),
        pk=pk,
    )
    if remove:
        Bookmark.objects.filter(user=request.user, message=message).delete()
        messages.info(request, _("Your bookmark has been removed"))
    else:

        try:
            Bookmark.objects.create(
                user=request.user, community=request.community, content_object=message,
            )
            messages.success(request, _("You have bookmarked this message"))
        except IntegrityError:
            pass

    return (
        TurboFrame(f"message-{message.id}-bookmark")
        .template(
            "private_messages/includes/bookmark.html",
            {"object": message, "has_bookmarked": not (remove)},
        )
        .response(request)
    )


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def message_delete_view(request, pk):

    message = get_object_or_404(
        Message.objects.for_community(request.community).for_sender_or_recipient(
            request.user
        ),
        pk=pk,
    )

    message.soft_delete(request.user)

    messages.info(request, _("Message has been deleted"))

    if "redirect" in request.POST:
        return redirect(
            "private_messages:inbox"
            if message.recipient == request.user
            else "private_messages:outbox"
        )

    return TurboStream(f"message-{pk}").remove.response()
