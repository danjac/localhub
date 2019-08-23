# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import (
    FormView,
    DeleteView,
    DetailView,
    ListView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.models import Community
from localhub.communities.views import CommunityRequiredMixin
from localhub.conversations.forms import MessageForm
from localhub.conversations.models import Message
from localhub.conversations.notifications import send_message_notifications
from localhub.core.types import BreadcrumbList, ContextDict
from localhub.core.views import BreadcrumbsMixin, SearchMixin
from localhub.users.utils import user_display
from localhub.users.views import UserSlugMixin


class MessageQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
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

    template_name = "conversations/inbox.html"

    def get_queryset(self) -> QuerySet:
        qs = (
            super()
            .get_queryset()
            .with_num_replies()
            .filter(recipient=self.request.user)
            .select_related("sender", "parent", "community")
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by(F("read").desc(nulls_first=True), "-created")


inbox_view = InboxView.as_view()


class OutboxView(MessageListView):
    """
    Messages sent by current user
    """

    template_name = "conversations/outbox.html"

    def get_queryset(self) -> QuerySet:
        qs = (
            super()
            .get_queryset()
            .with_num_replies()
            .filter(sender=self.request.user)
            .select_related("recipient", "parent", "community")
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


class ConversationView(SingleUserMixin, MessageListView):
    """
    Renders thread of conversation between two users.
    """

    template_name = "conversations/conversation.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(queryset=self.get_user_queryset())
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        qs = (
            Message.objects.with_num_replies()
            .filter(
                Q(Q(recipient=self.object) | Q(sender=self.object))
                & Q(
                    Q(recipient=self.request.user)
                    | Q(sender=self.request.user)
                ),
                community=self.request.community,
            )
            .select_related("sender", "recipient", "parent", "community")
            .distinct()
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by("-created")


conversation_view = ConversationView.as_view()


class MessageFormView(
    CommunityRequiredMixin, PermissionRequiredMixin, FormView
):

    permission_required = "conversations.create_message"
    template_name = "conversations/message_form.html"
    form_class = MessageForm

    def get_permission_object(self) -> Community:
        return self.request.community


class MessageReplyView(SingleObjectMixin, BreadcrumbsMixin, MessageFormView):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

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

    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("conversations:inbox"), _("Inbox")),
            (
                reverse(
                    "conversations:conversation",
                    args=[self.parent.sender.username],
                ),
                user_display(self.parent.sender),
            ),
            (self.parent.get_absolute_url(), self.parent.get_abbreviation()),
            ("#", _("Reply")),
        ]

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        data["parent"] = self.parent
        return data

    def get_initial(self) -> ContextDict:
        initial = super().get_initial()
        initial["message"] = "\n".join(
            [f"> {line}" for line in self.parent.message.splitlines()]
        )
        return initial

    def get_success_url(self) -> str:
        return reverse(
            "conversations:conversation",
            args=[self.message.recipient.username],
        )

    def form_valid(self, form) -> HttpResponse:
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
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.recipient = self.object = self.get_object(
            queryset=self.get_user_queryset()
        )
        if self.recipient.blocked.filter(pk=request.user.id):
            raise PermissionDenied(
                _("You are not permitted to send messages to this user")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("conversations:outbox"), _("Outbox")),
            (
                reverse(
                    "conversations:conversation",
                    args=[self.recipient.username],
                ),
                user_display(self.recipient),
            ),
            ("#", _("Send Message")),
        ]

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        return data

    def get_success_url(self) -> str:
        return reverse(
            "conversations:conversation",
            args=[self.message.recipient.username],
        )

    def form_valid(self, form) -> HttpResponse:
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
    def get_breadcrumbs(self) -> BreadcrumbList:
        if self.request.user == self.object.sender:
            breadcrumbs = [
                (reverse("conversations:outbox"), _("Outbox")),
                (
                    reverse(
                        "conversations:conversation",
                        args=[self.object.recipient.username],
                    ),
                    user_display(self.object.recipient),
                ),
            ]
        else:
            breadcrumbs = [
                (reverse("conversations:inbox"), _("Inbox")),
                (
                    reverse(
                        "conversations:conversation",
                        args=[self.object.sender.username],
                    ),
                    user_display(self.object.sender),
                ),
            ]

        if self.object.parent:
            breadcrumbs.append(
                (
                    self.object.parent.get_absolute_url(),
                    self.object.parent.get_abbreviation(),
                )
            )

        breadcrumbs.append(("#", self.object.get_abbreviation()))
        return breadcrumbs

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                Q(recipient=self.request.user) | Q(sender=self.request.user)
            )
            .select_related("recipient", "sender", "parent", "community")
        )

    def get_replies(self) -> QuerySet:
        return (
            self.object.replies.with_num_replies()
            .order_by("created")
            .select_related("recipient", "sender", "parent", "community")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["replies"] = self.get_replies()
        blocked = (
            self.object.recipient.blocked
            if self.object.sender == self.request.user
            else self.object.sender.blocked
        )
        data["can_reply"] = (
            self.request.user.has_perm(
                "conversations.create_message", self.request.community
            )
            and not blocked.filter(pk=self.request.user.pk).exists()
        )

        return data


message_detail_view = MessageDetailView.as_view()


class MessageDeleteView(MessageQuerySetMixin, DeleteView):
    def get_success_url(self) -> str:
        return reverse("conversations:outbox")

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(sender=self.request.user)


message_delete_view = MessageDeleteView.as_view()


class MessageMarkReadView(MessageQuerySetMixin, SingleObjectMixin, View):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(recipient=self.request.user, read__isnull=True)
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        message = self.get_object()
        message.read = timezone.now()
        message.save()
        return HttpResponseRedirect(message.get_absolute_url())


message_mark_read_view = MessageMarkReadView.as_view()
