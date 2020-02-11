# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import View
from rules.contrib.views import PermissionRequiredMixin
from vanilla import (
    DeleteView,
    DetailView,
    FormView,
    GenericModelView,
    ListView,
)

from localhub.communities.views import CommunityRequiredMixin
from localhub.users.utils import user_display
from localhub.views import BreadcrumbsMixin, SearchMixin

from .forms import MessageForm
from .models import Message
from .notifications import send_message_notifications


class MessageQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return (
            Message.objects.for_community(community=self.request.community)
            .exclude_blocked(self.request.user)
            .select_related(
                "sender",
                "recipient",
                "community",
                "parent",
                "parent__sender",
                "thread",
                "thread__sender",
            )
        )


class SenderQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_sender(self.request.user)


class RecipientQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_recipient(self.request.user)


class BaseMessageListView(SearchMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE


class InboxView(RecipientQuerySetMixin, BaseMessageListView):
    """
    Messages received by current user
    oere we should show the sender, timestamp...
    """

    template_name = "private_messages/inbox.html"

    def get_queryset(self):
        qs = super().get_queryset().with_has_thread(self.request.user)
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
        qs = super().get_queryset().with_has_thread(self.request.user)
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


class BaseMessageFormView(PermissionRequiredMixin, FormView):

    permission_required = "private_messages.create_message"
    template_name = "private_messages/message_form.html"
    form_class = MessageForm

    def get_permission_object(self):
        return self.request.community


class MessageReplyView(BreadcrumbsMixin, RecipientQuerySetMixin, BaseMessageFormView):
    @cached_property
    def parent(self):
        return get_object_or_404(
            self.get_queryset().exclude(sender__pk=self.request.user.id),
            pk=self.kwargs["pk"],
        )

    @cached_property
    def recipient(self):
        return self.parent.sender

    def get_breadcrumbs(self):
        return [
            (
                reverse("users:messages", args=[self.recipient.username]),
                user_display(self.recipient),
            ),
            (self.parent.get_absolute_url(), self.parent.abbreviate()),
            (None, _("Reply")),
        ]

    def get_form(self, data=None, files=None):
        form = self.form_class(data, files)
        form["message"].label = _("Reply to %(recipient)s") % {
            "recipient": user_display(self.recipient)
        }
        form["message"].initial = "\n".join(
            ["> " + line for line in self.parent.message.splitlines()]
        )
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        data["recipient"] = self.recipient
        return data

    def form_valid(self, form):
        message = form.save(commit=False)
        message.community = self.request.community
        message.sender = self.request.user
        message.recipient = self.recipient
        message.parent = self.parent
        message.thread = self.parent.thread or self.parent
        message.save()
        messages.success(
            self.request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": user_display(message.recipient)},
        )
        send_message_notifications(message)
        return redirect(message)


message_reply_view = MessageReplyView.as_view()


class MessageCreateView(BreadcrumbsMixin, CommunityRequiredMixin, BaseMessageFormView):
    @cached_property
    def recipient(self):
        return get_object_or_404(
            get_user_model()
            .objects.exclude(pk=self.request.user.id)
            .exclude(blockers=self.request.user)
            .exclude(blocked=self.request.user)
            .for_community(self.request.community),
            username=self.kwargs["slug"],
        )

    def get_breadcrumbs(self):
        return [
            (
                reverse("users:messages", args=[self.recipient.username]),
                user_display(self.recipient),
            ),
            (None, _("Send Message")),
        ]

    def get_form(self, data=None, files=None):
        form = self.form_class(data, files)
        form["message"].label = _("Send message to %(recipient)s") % {
            "recipient": user_display(self.recipient)
        }
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        return data

    def form_valid(self, form):
        message = form.save(commit=False)
        message.community = self.request.community
        message.sender = self.request.user
        message.recipient = self.recipient
        message.save()
        messages.success(
            self.request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": user_display(message.recipient)},
        )
        send_message_notifications(message)
        return redirect(message)


message_create_view = MessageCreateView.as_view()


class MessageDetailView(MessageQuerySetMixin, DetailView):

    model = Message

    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        if self.object.recipient == self.request.user and not self.object.read:
            self.object.read = timezone.now()
            self.object.save()
        return response

    def get_queryset(self):
        return super().get_queryset().for_sender_or_recipient(self.request.user)

    def get_replies(self):
        return self.get_queryset().filter(thread=self.object).order_by("created")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "replies": self.get_replies(),
            }
        )

        return data


message_detail_view = MessageDetailView.as_view()


class MessageDeleteView(SenderQuerySetMixin, DeleteView):
    model = Message

    def get_success_url(self):
        return reverse("private_messages:outbox")


message_delete_view = MessageDeleteView.as_view()


class MessageHideView(RecipientQuerySetMixin, GenericModelView):
    """
    "Removes" message by marking it hidden. Also marks it read. Removes
    message from view for recipient, but does not delete it completely.
    """

    def post(self, request, *args, **kwargs):
        message = self.get_object()
        if not message.read:
            message.read = timezone.now()
        message.is_hidden = True
        message.save()
        return redirect(message)


message_hide_view = MessageHideView.as_view()


class MessageMarkReadView(RecipientQuerySetMixin, GenericModelView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        message = self.get_object()
        message.read = timezone.now()
        message.save()
        return redirect(message)


message_mark_read_view = MessageMarkReadView.as_view()


class MessageMarkAllReadView(RecipientQuerySetMixin, View):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.get_queryset().update(read=timezone.now())
        return redirect("private_messages:inbox")


message_mark_all_read_view = MessageMarkAllReadView.as_view()
