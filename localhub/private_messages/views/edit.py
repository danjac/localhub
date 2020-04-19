# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.views import CommunityRequiredMixin
from localhub.users.utils import user_display
from localhub.views import SuccessFormView

from ..forms import MessageForm
from .mixins import RecipientQuerySetMixin, SenderQuerySetMixin


class BaseMessageFormView(PermissionRequiredMixin, SuccessFormView):

    permission_required = "private_messages.create_message"
    template_name = "private_messages/message_form.html"
    form_class = MessageForm

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return _("Your message has been sent to %(recipient)s") % {
            "recipient": user_display(self.object.recipient)
        }

    @cached_property
    def recipient(self):
        return self.get_recipient()

    def get_recipient(self):
        return None

    @cached_property
    def recipient_display(self):
        return user_display(self.recipient) if self.recipient else None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.recipient:
            kwargs.update(
                {"community": self.request.community, "sender": self.request.user}
            )

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.recipient:
            del form.fields["recipient"]
            form["message"].label = _(
                "Send message to %(recipient)s" % {"recipient": self.recipient_display}
            )
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["recipient"] = self.recipient
        data["recipient_display"] = self.recipient_display
        return data


class BaseReplyFormView(BaseMessageFormView):
    @cached_property
    def parent(self):
        parent = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        if parent.recipient == self.request.user:
            parent.mark_read()
        return parent

    def get_recipient(self):
        return self.parent.get_other_user(self.request.user)

    def notify(self):
        """Handle any notifications to recipient here"""
        ...

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        return data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.recipient
        self.object.parent = self.parent
        self.object.save()

        self.notify()

        return self.success_response()


class MessageReplyView(RecipientQuerySetMixin, BaseReplyFormView):
    def notify(self):
        self.object.notify_on_reply()


message_reply_view = MessageReplyView.as_view()


class MessageFollowUpView(SenderQuerySetMixin, BaseReplyFormView):
    def notify(self):
        self.object.notify_on_follow_up()


message_follow_up_view = MessageFollowUpView.as_view()


class MessageCreateView(
    CommunityRequiredMixin, BaseMessageFormView,
):
    def get_recipient(self):
        if "username" in self.kwargs:
            return get_object_or_404(
                get_user_model()
                .objects.exclude(pk=self.request.user.id)
                .for_community(self.request.community)
                .exclude_blocking(self.request.user),
                username=self.kwargs["username"],
            )
        return None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        if self.recipient:
            self.object.recipient = self.recipient
        self.object.save()

        self.object.notify_on_send()

        return self.success_response()


message_create_view = MessageCreateView.as_view()
