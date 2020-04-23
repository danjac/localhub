# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.views import CommunityRequiredMixin
from localhub.views import ParentObjectMixin, SuccessFormView

from ..forms import MessageForm, MessageRecipientForm
from .mixins import RecipientQuerySetMixin, SenderQuerySetMixin


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

    parent_object_name = "recipient"
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
            % {"recipient": self.recipient.get_display_name()}
        )
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.recipient
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
        kwargs = super().get_form_kwargs()

        kwargs.update(
            {"community": self.request.community, "sender": self.request.user}
        )

        return kwargs


message_create_view = MessageCreateView.as_view()
