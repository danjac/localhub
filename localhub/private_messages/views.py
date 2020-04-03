# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import View
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView, DetailView, FormView, GenericModelView, ListView

from localhub.bookmarks.models import Bookmark
from localhub.communities.views import CommunityRequiredMixin
from localhub.users.utils import user_display
from localhub.views import SearchMixin, SuccessMixin

from .forms import MessageForm
from .models import Message


class MessageQuerySetMixin(CommunityRequiredMixin):
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


class BaseMessageListView(SearchMixin, ListView):
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE


class BaseMessageActionView(SuccessMixin, GenericModelView):
    ...


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


class BaseMessageFormView(PermissionRequiredMixin, SuccessMixin, FormView):

    permission_required = "private_messages.create_message"
    template_name = "private_messages/message_form.html"
    form_class = MessageForm

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return _("Your message has been sent to %(recipient)s") % {
            "recipient": self.recipient_display
        }

    @cached_property
    def recipient(self):
        return self.get_recipient()

    def get_recipient(self):
        raise NotImplementedError

    @cached_property
    def recipient_display(self):
        return user_display(self.recipient)

    def get_form(self, data=None, files=None):
        form = self.form_class(data, files)
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
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_recipient(self):
        return self.parent.get_other_user(self.request.user)

    def notify(self):
        """Handle any notifications to recipient here"""
        ...

    def get_form(self, data=None, files=None):
        form = self.form_class(data, files)
        form["message"].initial = "\n".join(
            ["> " + line for line in self.parent.message.splitlines()]
        )
        return form

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

        if self.parent.recipient == self.request.user:
            self.parent.mark_read()

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
        return get_object_or_404(
            get_user_model()
            .objects.exclude(pk=self.request.user.id)
            .exclude(blockers=self.request.user)
            .exclude(blocked=self.request.user)
            .for_community(self.request.community),
            username=self.kwargs["username"],
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.community = self.request.community
        self.object.sender = self.request.user
        self.object.recipient = self.recipient
        self.object.save()

        self.object.notify_on_send()

        return self.success_response()


message_create_view = MessageCreateView.as_view()


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
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "replies": self.get_replies(),
                "parent": self.object.get_parent(self.request.user),
                "other_user": self.object.get_other_user(self.request.user),
            }
        )

        return data


message_detail_view = MessageDetailView.as_view()


class MessageDeleteView(SenderOrRecipientQuerySetMixin, SuccessMixin, DeleteView):
    """
    Does a "soft delete" which sets sender/recipient deleted flag
    accordingly.

    If both sender and recipient have soft-deleted, then the message
    is "hard" deleted.
    """

    model = Message
    success_message = _("This message has been deleted")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete(self.request.user)
        return self.success_response()

    def get_success_url(self):
        if self.request.user == self.object.recipient:
            return reverse("private_messages:inbox")
        return reverse("private_messages:outbox")


message_delete_view = MessageDeleteView.as_view()


class MessageMarkReadView(RecipientQuerySetMixin, BaseMessageActionView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mark_read()
        return self.success_response()


message_mark_read_view = MessageMarkReadView.as_view()


class MessageMarkAllReadView(RecipientQuerySetMixin, View):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.get_queryset().for_recipient(self.request.user).mark_read()
        return HttpResponseRedirect(reverse("private_messages:inbox"))


message_mark_all_read_view = MessageMarkAllReadView.as_view()


class MessageBookmarkView(SenderOrRecipientQuerySetMixin, BaseMessageActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()


message_bookmark_view = MessageBookmarkView.as_view()


class MessageRemoveBookmarkView(SenderOrRecipientQuerySetMixin, BaseMessageActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Bookmark.objects.filter(user=request.user, message=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


message_remove_bookmark_view = MessageRemoveBookmarkView.as_view()
