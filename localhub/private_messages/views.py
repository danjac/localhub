# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import F
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.communities.views import CommunityRequiredMixin
from localhub.views import (
    ParentObjectMixin,
    SearchMixin,
    SuccessActionView,
    SuccessDeleteView,
    SuccessFormView,
    SuccessView,
)

# Local
from .forms import MessageForm, MessageRecipientForm
from .models import Message


class MessageQuerySetMixin(
    LoginRequiredMixin, PermissionRequiredMixin, CommunityRequiredMixin
):
    permission_required = "private_messages.view_messages"

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        return (
            Message.objects.for_community(community=self.request.community)
            .exclude_blocked(self.request.user)
            .common_select_related()
        )


class SenderQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_sender(self.request.user)


class RecipientQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_recipient(self.request.user)


class SenderOrRecipientQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_sender_or_recipient(self.request.user)


class BaseMessageFormView(PermissionRequiredMixin, SuccessFormView):

    permission_required = "private_messages.create_message"
    template_name = "private_messages/message_form.html"
    form_class = MessageForm

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return _("Your message has been sent to %(recipient)s") % {
            "recipient": self.object.recipient.get_display_name()
        }


class BaseReplyFormView(ParentObjectMixin, BaseMessageFormView):
    @cached_property
    def recipient(self):
        return self.parent.get_other_user(self.request.user)

    def get_parent_queryset(self):
        return self.get_queryset()

    def notify(self):
        """Handle any notifications to recipient here"""
        ...

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.recipient
        self.object.parent = self.parent
        self.object.save()

        self.notify()

        return self.success_response()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        return data


class MessageReplyView(RecipientQuerySetMixin, BaseReplyFormView):
    def notify(self):
        self.object.notify_on_reply()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form["message"].label = _(
            "Send reply to %(recipient)s"
            % {"recipient": self.recipient.get_display_name()}
        )
        return form


message_reply_view = MessageReplyView.as_view()


class MessageFollowUpView(SenderQuerySetMixin, BaseReplyFormView):
    def notify(self):
        self.object.notify_on_follow_up()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form["message"].label = _(
            "Send follow-up to %(recipient)s"
            % {"recipient": self.recipient.get_display_name()}
        )
        return form


message_follow_up_view = MessageFollowUpView.as_view()


class MessageRecipientCreateView(
    CommunityRequiredMixin, ParentObjectMixin, BaseMessageFormView,
):
    """Send new message to a specific recipient"""

    parent_context_object_name = "recipient"
    parent_slug_kwarg = "username"
    parent_slug_field = "username"

    def get_parent_queryset(self):
        return (
            get_user_model()
            .objects.exclude(pk=self.request.user.id)
            .for_community(self.request.community)
            .exclude_blocking(self.request.user)
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form["message"].label = _(
            "Send message to %(recipient)s"
            % {"recipient": self.parent.get_display_name()}
        )
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.parent
        self.object.save()

        self.object.notify_on_send()

        return self.success_response()


message_recipient_create_view = MessageRecipientCreateView.as_view()


class MessageCreateView(
    CommunityRequiredMixin, BaseMessageFormView,
):
    """
    Send message to any individual recipient
    """

    form_class = MessageRecipientForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.save()

        self.object.notify_on_send()

        return self.success_response()

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            **{"community": self.request.community, "sender": self.request.user},
        }


message_create_view = MessageCreateView.as_view()


class BaseMessageListView(SearchMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE


class InboxView(RecipientQuerySetMixin, BaseMessageListView):
    """
    Messages received by current user
    oere we should show the sender, timestamp...
    """

    template_name = "private_messages/inbox.html"

    def get_queryset(self):
        qs = super().get_queryset().with_has_bookmarked(self.request.user)
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by(F("read").desc(nulls_first=True), "-created")


inbox_view = InboxView.as_view()


class OutboxView(SenderQuerySetMixin, BaseMessageListView):
    """
    Messages sent by current user
    """

    template_name = "private_messages/outbox.html"

    def get_queryset(self):
        qs = super().get_queryset().with_has_bookmarked(self.request.user)
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


class MessageDetailView(SenderOrRecipientQuerySetMixin, DetailView):

    model = Message

    def get_queryset(self):
        return super().get_queryset().with_has_bookmarked(self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.recipient == self.request.user:
            obj.mark_read(mark_replies=True)
        return obj

    def get_replies(self):
        return (
            self.object.get_all_replies()
            .for_sender_or_recipient(self.request.user)
            .common_select_related()
            .order_by("created")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "replies": self.get_replies(),
                "parent": self.object.get_parent(self.request.user),
                "other_user": self.object.get_other_user(self.request.user),
            },
        }


message_detail_view = MessageDetailView.as_view()


class MessageMarkAllReadView(RecipientQuerySetMixin, SuccessView):
    success_url = reverse_lazy("private_messages:inbox")

    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.get_queryset().for_recipient(self.request.user).mark_read()
        return self.success_response()


message_mark_all_read_view = MessageMarkAllReadView.as_view()


class MessageMarkReadView(RecipientQuerySetMixin, SuccessActionView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.object.mark_read()
        return self.success_response()


message_mark_read_view = MessageMarkReadView.as_view()


class BaseMessageBookmarkView(SenderOrRecipientQuerySetMixin, SuccessActionView):
    is_success_ajax_response = True
    success_template_name = "private_messages/includes/bookmark.html"


class MessageBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have bookmarked this message")

    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        return self.success_response()

    def get_success_context_data(self):
        return {
            **super().get_success_context_data(),
            "has_bookmarked": True,
        }


message_bookmark_view = MessageBookmarkView.as_view()


class MessageRemoveBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have removed this message from your bookmarks")

    def post(self, request, *args, **kwargs):
        Bookmark.objects.filter(user=request.user, message=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_context_data(self):
        return {
            **super().get_success_context_data(),
            "has_bookmarked": False,
        }


message_remove_bookmark_view = MessageRemoveBookmarkView.as_view()


class MessageDeleteView(SenderOrRecipientQuerySetMixin, SuccessDeleteView):
    """
    Does a "soft delete" which sets sender/recipient deleted flag
    accordingly.

    If both sender and recipient have soft-deleted, then the message
    is "hard" deleted.
    """

    model = Message
    success_message = _("You have deleted this message")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete(self.request.user)
        return self.success_response()

    def get_success_url(self):
        if self.request.user == self.object.recipient:
            return reverse("private_messages:inbox")
        return reverse("private_messages:outbox")


message_delete_view = MessageDeleteView.as_view()
