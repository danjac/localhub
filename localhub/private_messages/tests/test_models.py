# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.utils import timezone

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.notifications.factories import NotificationFactory
from localhub.users.factories import UserFactory

from ..factories import MessageFactory
from ..models import Message

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_for_community(self, community):

        message = MessageFactory(
            community=community,
            sender=MembershipFactory(community=community).member,
            recipient=MembershipFactory(community=community).member,
        )

        qs = Message.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == message

    def test_mark_read(self):
        message = MessageFactory()
        notification = NotificationFactory(content_object=message)

        Message.objects.mark_read()
        message.refresh_from_db()
        notification.refresh_from_db()

        assert notification.is_read
        assert message.read

    def test_unread_if_read(self):
        MessageFactory(read=timezone.now())
        assert not Message.objects.unread().exists()

    def test_unread_if_unread(self):
        MessageFactory(read=None)
        assert Message.objects.unread().exists()

    def test_for_community_if_recipient_not_member(self, community):
        MessageFactory(sender=MembershipFactory(community=community).member)
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_sender_inactive(self, community):
        MessageFactory(
            sender=MembershipFactory(community=community, active=False).member,
            recipient=MembershipFactory(community=community).member,
        )
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_sender_not_member(self, community):
        MessageFactory(
            sender=MembershipFactory(community=CommunityFactory(), active=True).member,
            recipient=MembershipFactory(community=community).member,
        )
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_neither_member(self, community):
        MessageFactory(community=community)
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_not_community_message(self, community):
        MessageFactory()
        assert not Message.objects.for_community(community).exists()

    def test_exclude_sender_blocked_if_sender_blocking(self):
        message = MessageFactory()
        message.sender.blocked.add(message.recipient)

        assert Message.objects.exclude_sender_blocked(message.recipient).count() == 0

    def test_exclude_sender_blocked_if_sender_blocked(self):
        message = MessageFactory()
        message.sender.blockers.add(message.recipient)

        assert Message.objects.exclude_sender_blocked(message.recipient).count() == 0

    def test_exclude_sender_blocked_if_not_blocked(self):
        message = MessageFactory()

        assert Message.objects.exclude_sender_blocked(message.recipient).count() == 1

    def test_exclude_recipient_blocked_if_recipient_blocking(self):
        message = MessageFactory()
        message.recipient.blocked.add(message.sender)

        assert Message.objects.exclude_recipient_blocked(message.sender).count() == 0

    def test_exclude_recipient_blocked_if_recipient_blocked(self):
        message = MessageFactory()
        message.recipient.blockers.add(message.sender)

        assert Message.objects.exclude_recipient_blocked(message.sender).count() == 0

    def test_exclude_blocked_by_recipient_if_not_blocked(self):
        message = MessageFactory()

        assert Message.objects.exclude_recipient_blocked(message.sender).count() == 1

    def test_exclude_blocked_if_sender_blocked(self, user):

        message = MessageFactory()
        message.sender.blocked.add(user)

        assert Message.objects.exclude_blocked(user).count() == 0

    def test_exclude_blocked_if_recipient_blocked(self, user):
        message = MessageFactory()
        message.recipient.blocked.add(user)

        assert Message.objects.exclude_blocked(user).count() == 0

    def test_exclude_blocked_if_neither_blocked(self, user):
        MessageFactory()

        assert Message.objects.exclude_blocked(user).count() == 1

    def test_exclude_blocked_if_both_blocked(self, user):
        message = MessageFactory()
        message.recipient.blocked.add(user)
        message.sender.blocked.add(user)

        assert Message.objects.exclude_blocked(user).count() == 0

    def test_for_sender(self, user):
        MessageFactory(sender=user)
        assert Message.objects.for_sender(user).exists()

    def test_for_recipient(self, user):
        MessageFactory(recipient=user)
        assert Message.objects.for_recipient(user).exists()

    def test_from_sender_to_recipient(self, user):
        message = MessageFactory(recipient=user)
        assert Message.objects.from_sender_to_recipient(message.sender, user).exists()
        assert not Message.objects.from_sender_to_recipient(
            user, message.recipient
        ).exists()

    def test_for_sender_if_sender_deleted(self, user):
        MessageFactory(sender=user, sender_deleted=timezone.now())
        assert not Message.objects.for_sender(user).exists()

    def test_for_sender_if_recipient_deleted(self, user):
        MessageFactory(sender=user, recipient_deleted=timezone.now())
        assert Message.objects.for_sender(user).exists()

    def test_for_recipient_if_recipient_deleted(self, user):
        MessageFactory(recipient=user, recipient_deleted=timezone.now())
        assert not Message.objects.for_recipient(user).exists()

    def test_for_recipient_if_sender_deleted(self, user):
        MessageFactory(recipient=user, sender_deleted=timezone.now())
        assert Message.objects.for_recipient(user).exists()

    def test_for_sender_or_recipient(self, user):

        first = MessageFactory(sender=user)
        second = MessageFactory(recipient=user)
        third = MessageFactory()
        fourth = MessageFactory(recipient=user, recipient_deleted=timezone.now())
        fifth = MessageFactory(sender=user, sender_deleted=timezone.now())

        messages = Message.objects.for_sender_or_recipient(user)
        assert first in messages
        assert second in messages
        assert third not in messages
        assert fourth not in messages
        assert fifth not in messages

    def test_with_num_replies_if_recipient(self, user):
        first = MessageFactory(sender=user)
        MessageFactory(recipient=user, parent=first)

        message = Message.objects.with_num_replies(user).get(pk=first.id)
        assert message.num_replies == 1

    def test_with_num_replies_if_sender(self, user):
        first = MessageFactory(sender=user)
        MessageFactory(sender=user, parent=first)

        message = Message.objects.with_num_replies(user).get(pk=first.id)
        assert message.num_replies is None

    def test_with_num_replies_if_no_replies(self, user):

        first = MessageFactory(sender=user)

        message = Message.objects.with_num_replies(user).get(pk=first.id)
        assert message.num_replies is None

    def test_with_num_follow_ups_if_sender(self, user):

        first = MessageFactory(sender=user)
        MessageFactory(sender=user, parent=first)

        message = Message.objects.with_num_follow_ups(user).get(pk=first.id)
        assert message.num_follow_ups == 1

    def test_with_num_follow_ups_if_sender_deleted(self, user):
        first = MessageFactory(sender=user)
        MessageFactory(sender=user, parent=first, sender_deleted=timezone.now())

        message = Message.objects.with_num_follow_ups(user).get(pk=first.id)
        assert message.num_follow_ups is None

    def test_with_num_follow_ups_if_recipient(self, user):
        first = MessageFactory(sender=user)
        MessageFactory(recipient=user, parent=first)

        message = Message.objects.with_num_follow_ups(user).get(pk=first.id)
        assert message.num_follow_ups is None

    def test_with_num_follow_ups_if_no_follow_ups(self, user):

        first = MessageFactory(sender=user)

        message = Message.objects.with_num_follow_ups(user).get(pk=first.id)
        assert message.num_follow_ups is None

    def test_with_common_annotations(self, user):
        first = MessageFactory(sender=user)
        MessageFactory(recipient=user, parent=first)
        MessageFactory(sender=user, parent=first)

        message = Message.objects.with_common_annotations(user).get(pk=first.id)
        assert message.num_replies == 1
        assert message.num_follow_ups == 1

    def test_between(self):

        user_a = UserFactory()
        user_b = UserFactory()

        first = MessageFactory(sender=user_a, recipient=user_b)
        second = MessageFactory(recipient=user_a, sender=user_b)
        third = MessageFactory()
        fourth = MessageFactory(sender=user_a)
        fifth = MessageFactory(sender=user_b)
        sixth = MessageFactory(recipient=user_a)
        seventh = MessageFactory(recipient=user_b)
        eighth = MessageFactory(
            recipient=user_a, sender=user_b, recipient_deleted=timezone.now()
        )
        ninth = MessageFactory(
            sender=user_a, recipient=user_b, sender_deleted=timezone.now()
        )
        tenth = MessageFactory(
            sender=user_a, recipient=user_b, recipient_deleted=timezone.now()
        )
        eleventh = MessageFactory(
            recipient=user_a, sender=user_b, sender_deleted=timezone.now()
        )

        messages = Message.objects.between(user_a, user_b)

        assert first in messages
        assert second in messages
        assert third not in messages
        assert fourth not in messages
        assert fifth not in messages
        assert sixth not in messages
        assert seventh not in messages
        assert eighth not in messages
        assert ninth not in messages
        assert tenth in messages
        assert eleventh in messages

    def test_notifications(self, message):
        notification = NotificationFactory(content_object=message)
        # check we just include the one
        NotificationFactory()
        NotificationFactory(content_object=MessageFactory())

        notifications = Message.objects.filter(pk=message.id).notifications()
        assert notifications.count() == 1
        assert notifications.first() == notification


class TestMessageModel:
    def test_resolve_url_if_no_thread(self, user):
        message = MessageFactory(sender=user)
        assert message.resolve_url(user) == message.get_absolute_url()

    def test_resolve_url_if_is_thread(self, user):
        message = MessageFactory(sender=user)
        assert message.resolve_url(user, is_thread=True) == f"#message-{message.id}"

    def test_resolve_url_if_has_thread(self, user):
        thread = MessageFactory(recipient=user)
        message = MessageFactory(sender=user, thread=thread)
        assert (
            message.resolve_url(user)
            == f"{thread.get_absolute_url()}#message-{message.id}"
        )

    def test_get_parent_if_none(self, user):
        message = MessageFactory(sender=user)
        assert message.get_parent(user) is None

    def test_get_parent_if_not_visible(self, user):
        parent = MessageFactory(recipient=user, recipient_deleted=timezone.now())
        message = MessageFactory(sender=user, parent=parent)
        assert message.get_parent(user) is None

    def test_get_parent_if_visible(self, user):
        parent = MessageFactory(recipient=user)
        message = MessageFactory(sender=user, parent=parent)
        assert message.get_parent(user) == parent

    def test_get_thread_if_none(self, user):
        message = MessageFactory(sender=user)
        assert message.get_thread(user) is None

    def test_get_thread_if_not_visible(self, user):
        thread = MessageFactory(recipient=user, recipient_deleted=timezone.now())
        message = MessageFactory(sender=user, thread=thread)
        assert message.get_thread(user) is None

    def test_get_thread_if_visible(self, user):
        thread = MessageFactory(recipient=user)
        message = MessageFactory(sender=user, thread=thread)
        assert message.get_thread(user) == thread

    def test_is_visible_to_neither_sender_or_recipient(self, message):
        assert not message.is_visible(UserFactory())

    def test_is_visible_to_sender(self, message):
        assert message.is_visible(message.sender)

    def test_is_visible_to_sender_if_sender_deleted(self):
        message = MessageFactory(sender_deleted=timezone.now())
        assert not message.is_visible(message.sender)

    def test_is_visible_to_sender_if_recipient_deleted(self):
        message = MessageFactory(recipient_deleted=timezone.now())
        assert message.is_visible(message.sender)

    def test_is_visible_to_recipient(self, message):
        assert message.is_visible(message.recipient)

    def test_is_visible_to_recipient_if_recipient_deleted(self):
        message = MessageFactory(recipient_deleted=timezone.now())
        assert not message.is_visible(message.recipient)

    def test_is_visible_to_recipient_if_sender_deleted(self):
        message = MessageFactory(sender_deleted=timezone.now())
        assert message.is_visible(message.recipient)

    def test_get_other_user(self, message):
        assert message.get_other_user(message.sender) == message.recipient
        assert message.get_other_user(message.recipient) == message.sender

    def test_abbreviate_with_markdown(self):
        message = Message(message="Hello\nthis is a *test*")
        assert message.abbreviate() == "Hello this is a test"

    def test_abbreviate_long_message(self):
        message = Message(message="this is a test with more content")
        assert message.abbreviate(length=12) == "...more content"

    def test_mark_read(self):
        message = MessageFactory()
        notification = NotificationFactory(content_object=message)

        message.mark_read()
        message.refresh_from_db()
        notification.refresh_from_db()

        assert notification.is_read
        assert message.read

    def test_soft_delete_if_recipient(self, message):
        message.soft_delete(message.recipient)
        message.refresh_from_db()
        assert message.sender_deleted is None
        assert message.recipient_deleted is not None

    def test_soft_delete_if_sender(self, message):
        message.soft_delete(message.sender)
        message.refresh_from_db()
        assert message.sender_deleted is not None
        assert message.recipient_deleted is None

    def test_soft_delete_if_recipient_and_sender_already_deleted(self):
        message = MessageFactory(sender_deleted=timezone.now())
        message.soft_delete(message.recipient)
        assert not Message.objects.exists()

    def test_soft_delete_if_sender_and_recipient_already_deleted(self):
        message = MessageFactory(recipient_deleted=timezone.now())
        message.soft_delete(message.sender)
        assert not Message.objects.exists()

    def test_get_notifications(self, message):
        notification = NotificationFactory(content_object=message)
        # check we just include the one
        NotificationFactory()
        NotificationFactory(content_object=MessageFactory())

        notifications = message.get_notifications()
        assert notifications.count() == 1
        assert notifications.first() == notification

