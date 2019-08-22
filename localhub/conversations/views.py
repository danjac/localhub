# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
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
from localhub.core.types import ContextDict
from localhub.core.views import SearchMixin
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
            .filter(recipient=self.request.user)
            .select_related("sender")
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by("read", "-created")


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
            .filter(sender=self.request.user)
            .select_related("recipient")
        )
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


class ConversationView(SingleUserMixin, MessageListView):
    template_name = "conversations/conversation.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(queryset=self.get_user_queryset())
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        qs = Message.objects.filter(
            Q(Q(recipient=self.object) | Q(sender=self.object))
            & Q(Q(recipient=self.request.user) | Q(sender=self.request.user)),
            community=self.request.community,
        ).distinct()
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank")
        return qs.order_by("-created")

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if (
            self.request.user.has_perm(
                "conversations.create_message", self.request.community
            )
            and not self.object.blocked.filter(
                pk=self.request.user.id
            ).exists()
        ):
            data["message_form"] = MessageForm()

        return data


conversation_view = ConversationView.as_view()


class MessageCreateView(
    CommunityRequiredMixin, PermissionRequiredMixin, SingleUserMixin, FormView
):
    permission_required = "conversations.create_message"
    template_name = "conversations/message_form.html"
    form_class = MessageForm

    def get_permission_object(self) -> Community:
        return self.request.community

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.recipient = self.get_object(queryset=self.get_user_queryset())
        if self.recipient.blocked.filter(pk=request.user.id):
            raise PermissionDenied(
                _("You are not permitted to send messages to this user")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse(
            "conversations:conversation", args=[self.object.recipient.username]
        )

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.recipient
        self.object.save()
        messages.success(
            self.request,
            _("Message sent to %(recipient)s")
            % {"recipient": self.object.recipient},
        )
        send_message_notifications(self.object)
        return HttpResponseRedirect(self.get_success_url())


message_create_view = MessageCreateView.as_view()


class MessageDetailView(MessageQuerySetMixin, LoginRequiredMixin, DetailView):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                Q(recipient=self.request.user) | Q(sender=self.request.user)
            )
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.object.sender == self.request.user:
            data.update(
                {
                    "sender_url": reverse("conversations:outbox"),
                    "recipient_url": reverse(
                        "conversations:conversation",
                        args=[self.object.recipient.username],
                    ),
                }
            )
        else:
            data.update(
                {
                    "sender_url": reverse(
                        "conversations:conversation",
                        args=[self.object.recipient.username],
                    ),
                    "recipient_url": reverse("conversations:inbox"),
                }
            )
        return data


message_detail_view = MessageDetailView.as_view()


class MessageDeleteView(MessageQuerySetMixin, DeleteView):
    def get_success_url(self) -> str:
        return reverse(
            "conversations:conversation", args=[self.object.recipient.username]
        )

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
