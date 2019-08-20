# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.models import Community
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import BreadcrumbList, ContextDict
from localhub.core.views import BreadcrumbsMixin, SearchMixin
from localhub.messageboard.forms import MessageForm
from localhub.messageboard.models import Message, MessageRecipient
from localhub.messageboard.notifications import send_message_notifications
from localhub.users.utils import user_display
from localhub.users.views import SingleUserMixin


class MessageRecipientQuerySetMixin(
    LoginRequiredMixin, CommunityRequiredMixin
):
    def get_queryset(self) -> models.QuerySet:
        return MessageRecipient.objects.filter(
            recipient=self.request.user,
            message__community=self.request.community,
        ).select_related("message", "message__sender")


class MessageQuerySetMixin(LoginRequiredMixin, CommunityRequiredMixin):
    def get_queryset(self) -> models.QuerySet:
        return Message.objects.filter(
            sender=self.request.user, community=self.request.community
        ).select_related("parent", "parent__sender")


class MessageRecipientListView(
    MessageRecipientQuerySetMixin, SearchMixin, ListView
):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self) -> models.QuerySet:
        qs = super().get_queryset().order_by("-read", "-message__created")
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


message_recipient_list_view = MessageRecipientListView.as_view()


class SenderMessageRecipientListView(
    SingleUserMixin, BreadcrumbsMixin, MessageRecipientListView
):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    template_name = "messageboard/sender_messagerecipient_list.html"

    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("messageboard:message_recipient_list"), _("Inbox")),
            ("#", user_display(self.object)),
        ]

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(message__sender=self.object)


sender_message_recipient_list_view = SenderMessageRecipientListView.as_view()


class MessageRecipientDetailView(
    MessageRecipientQuerySetMixin, BreadcrumbsMixin, DetailView
):
    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("messageboard:message_recipient_list"), _("Inbox")),
            (
                reverse(
                    "messageboard:sender_message_recipient_list",
                    args=[self.object.message.sender.username],
                ),
                user_display(self.object.message.sender),
            ),
            ("#", self.object.message.subject),
        ]

    def get(self, *args, **kwargs) -> HttpResponse:
        response = super().get(*args, **kwargs)
        if not self.object.read:
            self.object.read = timezone.now()
            self.object.save(update_fields=["read"])
        return response

    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("message__parent", "message__parent__sender")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["replies"] = Message.objects.filter(
            sender=self.request.user, parent=self.object.message
        ).order_by("-created")
        return data


message_recipient_detail_view = MessageRecipientDetailView.as_view()


class MessageRecipientDeleteView(MessageRecipientQuerySetMixin, DeleteView):
    def get_success_url(self) -> str:
        return reverse("messageboard:message_recipient_list")


message_recipient_delete_view = MessageRecipientDeleteView.as_view()


class MessageListView(MessageQuerySetMixin, SearchMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self) -> models.QuerySet:
        qs = super().get_queryset().order_by("-created")
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


message_list_view = MessageListView.as_view()


class MessageDetailView(MessageQuerySetMixin, BreadcrumbsMixin, DetailView):
    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("messageboard:message_list"), _("Outbox")),
            ("#", self.object.subject),
        ]

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["recipients"] = self.object.messagerecipient_set.select_related(
            "recipient"
        ).order_by("recipient__name", "recipient__username")
        if self.object.parent:
            data["reply_to"] = (
                MessageRecipient.objects.filter(
                    recipient=self.request.user, message=self.object.parent
                )
                .select_related("message")
                .first()
            )
        return data


message_detail_view = MessageDetailView.as_view()


class MessageCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CommunityRequiredMixin,
    BreadcrumbsMixin,
    CreateView,
):
    model = Message
    form_class = MessageForm

    permission_required = "messageboard.create_message"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_breadcrumbs(self) -> BreadcrumbList:
        if not self.parent_recipient:
            return []
        return [
            (reverse("messageboard:message_recipient_list"), _("Inbox")),
            (self.parent_recipient.get_absolute_url(), self.parent.subject),
            ("#", _("Reply")),
        ]

    @cached_property
    def parent_recipient(self) -> Optional[MessageRecipient]:
        if self.parent is None:
            return None
        try:
            return MessageRecipient.objects.get(
                message=self.parent, recipient=self.request.user
            )
        except MessageRecipient.DoesNotExist:
            raise Http404

    @cached_property
    def parent(self) -> Optional[Message]:
        if "parent" not in self.kwargs:
            return None
        try:
            return (
                Message.objects.filter(
                    community=self.request.community,
                    messagerecipient__recipient=self.request.user,
                )
                .select_related("sender")
                .get(pk=self.kwargs["parent"])
            )
        except Message.DoesNotExist:
            raise Http404

    def get_initial(self) -> ContextDict:
        initial = super().get_initial()
        if self.parent:
            parent_message = "\n".join(
                [f"> {line}" for line in self.parent.message.split("\n")]
            )
            initial.update(
                {
                    "subject": f"RE: {self.parent.subject}",
                    "individuals": f"@{self.parent.sender.username}",
                    "message": parent_message,
                }
            )
        elif "username" in self.kwargs:
            initial.update({"individuals": f"@{self.kwargs['username']}"})

        return initial

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def get_success_message(self, num_recipients: int) -> str:
        if num_recipients == 1:
            return _("Your message has been sent")

        return _("Your message has been sent to %(num_recipients)s people") % {
            "num_recipients": num_recipients
        }

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.parent:
            data["recipient"] = MessageRecipient.objects.filter(
                message=self.parent, recipient=self.request.user
            ).first()
        return data

    def form_valid(self, form) -> HttpResponse:

        recipients = form.get_recipients(
            self.request.user, self.request.community
        )
        num_recipients = recipients.count()

        if num_recipients == 0:
            messages.error(
                self.request, _("Please select at least one valid recipient")
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)

        self.object.sender = self.request.user
        self.object.community = self.request.community
        self.object.parent = self.parent
        self.object.save()

        MessageRecipient.objects.bulk_create(
            [
                MessageRecipient(message=self.object, recipient=recipient)
                for recipient in recipients
            ],
            ignore_conflicts=True,
        )

        # fetch again so we have IDs
        for recipient in self.object.messagerecipient_set.select_related(
            "message", "message__community", "message__sender", "recipient"
        ):
            send_message_notifications(recipient)

        messages.success(
            self.request, self.get_success_message(num_recipients)
        )
        return HttpResponseRedirect(self.get_success_url())


message_create_view = MessageCreateView.as_view()
