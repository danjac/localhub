# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.views import CommunityRequiredMixin
from localhub.core.views import BreadcrumbsMixin, SearchMixin
from localhub.private_messages.forms import MessageForm
from localhub.private_messages.models import Message
from localhub.private_messages.notifications import send_message_notifications
from localhub.users.utils import user_display
from localhub.users.views import UserSlugMixin


class MessageQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Message.objects.filter(community=self.request.community)


class MessageListView(
    LoginRequiredMixin, MessageQuerySetMixin, SearchMixin, ListView
):
    paginate_by = settings.DEFAULT_PAGE_SIZE


class SingleUserMixin(UserSlugMixin, SingleObjectMixin):
    context_object_name = "user_obj"

    def get_user_queryset(self):
        return (
            get_user_model()
            .objects.exclude(pk=self.request.user.id)
            .active(self.request.community)
        )


class InboxView(MessageListView):
    """
    Messages received by current user
    Here we should show the sender, timestamp...
    """

    template_name = "private_messages/inbox.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .with_sender_has_blocked(self.request.user)
            .filter(recipient=self.request.user)
            .select_related(
                "sender", "recipient", "parent", "reply", "community"
            )
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by(F("read").desc(nulls_first=True), "-created")


inbox_view = InboxView.as_view()


class OutboxView(MessageListView):
    """
    Messages sent by current user
    """

    template_name = "private_messages/outbox.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(sender=self.request.user)
            .select_related(
                "sender", "recipient", "parent", "reply", "community"
            )
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


class MessageFormView(
    CommunityRequiredMixin, PermissionRequiredMixin, FormView
):

    permission_required = "private_messages.create_message"
    template_name = "private_messages/message_form.html"
    form_class = MessageForm

    def get_permission_object(self):
        return self.request.community


class MessageReplyView(SingleObjectMixin, BreadcrumbsMixin, MessageFormView):
    def dispatch(self, request, *args, **kwargs):

        self.parent = self.object = self.get_object(
            queryset=Message.objects.filter(
                recipient=self.request.user, community=self.request.community
            )
        )
        self.recipient = self.parent.sender

        if self.parent.sender.blocked.filter(pk=request.user.id):
            raise PermissionDenied(
                _("You are not permitted to send messages to this user")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self):
        return [
            (reverse("private_messages:inbox"), _("Inbox")),
            (self.parent.get_absolute_url(), self.parent.get_abbreviation()),
            ("#", _("Reply")),
        ]

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        data["parent"] = self.parent
        return data

    def get_initial(self):
        initial = super().get_initial()
        initial["message"] = "\n".join(
            [f"> {line}" for line in self.parent.message.splitlines()]
        )
        return initial

    def get_success_url(self):
        return self.message.get_absolute_url()

    def form_valid(self, form):
        self.message = form.save(commit=False)
        self.message.community = self.request.community
        self.message.sender = self.request.user
        self.message.recipient = self.recipient
        self.message.parent = self.parent
        self.message.save()

        messages.success(
            self.request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": user_display(self.message.recipient)},
        )
        send_message_notifications(self.message)
        return HttpResponseRedirect(self.get_success_url())


message_reply_view = MessageReplyView.as_view()


class MessageCreateView(SingleUserMixin, BreadcrumbsMixin, MessageFormView):
    def dispatch(self, request, *args, **kwargs):
        self.recipient = self.object = self.get_object(
            queryset=self.get_user_queryset()
        )
        if self.recipient.blocked.filter(pk=request.user.id):
            raise PermissionDenied(
                _("You are not permitted to send messages to this user")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self):
        return [
            (
                reverse("users:messages", args=[self.recipient.username]),
                user_display(self.recipient),
            ),
            ("#", _("Send Message")),
        ]

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        return data

    def get_success_url(self):
        return self.message.get_absolute_url()

    def form_valid(self, form):
        self.message = form.save(commit=False)
        self.message.community = self.request.community
        self.message.sender = self.request.user
        self.message.recipient = self.recipient
        self.message.save()
        messages.success(
            self.request,
            _("Your message has been sent to %(recipient)s")
            % {"recipient": user_display(self.message.recipient)},
        )
        send_message_notifications(self.message)
        return HttpResponseRedirect(self.get_success_url())


message_create_view = MessageCreateView.as_view()


class MessageDetailView(
    MessageQuerySetMixin, LoginRequiredMixin, BreadcrumbsMixin, DetailView
):
    """
    TBD:

    1) get the "thread" of messages where this object is the ancestor
    of the messages
    2) get the ancestor of the object, if any, and show as link (unless
    ancestor is just one level up, as we already have link to parent)

    To get the thread:
    1) call get_queryset() to get all messages belonging to both recipient+
    sender.
    2) exclude any with parent_id NULL, or created older than current object.
    3) for each in queryset, run a recursive function in Python to find
    any with ancestor = current object ID.

    To get the ancestor, we do the same in reverse:
    1) call get_queryset() and filter any newer than the current object, or
    parent_id is NOT NULL.
    2) call recursive function to find the ancestor.
    """

    def get_breadcrumbs(self):
        if self.request.user == self.object.sender:
            breadcrumbs = [(reverse("private_messages:outbox"), _("Outbox"))]
        else:
            breadcrumbs = [(reverse("private_messages:inbox"), _("Inbox"))]

        if self.object.parent:
            breadcrumbs.append(
                (
                    self.object.parent.get_absolute_url(),
                    self.object.parent.get_abbreviation(),
                )
            )

        breadcrumbs.append(("#", self.object.get_abbreviation()))
        return breadcrumbs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            # ensure reply has all fields
            if self.object.reply:
                data["reply"] = self.get_queryset().get(
                    pk=self.object.reply.id
                )
        except Message.DoesNotExist:
            pass
        return data

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_sender_has_blocked(self.request.user)
            .filter(
                Q(recipient=self.request.user) | Q(sender=self.request.user)
            )
            .select_related(
                "community", "parent", "recipient", "reply", "sender"
            )
        )


message_detail_view = MessageDetailView.as_view()


class MessageUpdateView(
    MessageQuerySetMixin, BreadcrumbsMixin, SuccessMessageMixin, UpdateView
):
    form_class = MessageForm

    def get_success_message(self, cleaned_data):
        return _("Your message has been updated")

    def get_breadcrumbs(self):
        return [
            (reverse("private_messages:outbox"), _("Outbox")),
            ("#", _("Edit Message")),
        ]

    def get_form(self):
        form = super().get_form()
        form.fields["message"].label = _("Edit Message")
        return form

    def get_queryset(self):
        return super().get_queryset().filter(sender=self.request.user)


message_update_view = MessageUpdateView.as_view()


class MessageDeleteView(MessageQuerySetMixin, DeleteView):
    def get_success_url(self):
        return reverse("private_messages:outbox")

    def get_queryset(self):
        return super().get_queryset().filter(sender=self.request.user)


message_delete_view = MessageDeleteView.as_view()


class MessageMarkReadView(MessageQuerySetMixin, SingleObjectMixin, View):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(recipient=self.request.user, read__isnull=True)
        )

    def post(self, request, *args, **kwargs):
        message = self.get_object()
        message.read = timezone.now()
        message.save()
        return HttpResponseRedirect(message.get_absolute_url())


message_mark_read_view = MessageMarkReadView.as_view()
