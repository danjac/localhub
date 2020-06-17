# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest
from pytest_django.asserts import assertTemplateUsed

# Social-BFG
from social_bfg.apps.comments.factories import CommentFactory
from social_bfg.apps.communities.factories import MembershipFactory
from social_bfg.apps.events.factories import EventFactory
from social_bfg.apps.likes.factories import LikeFactory
from social_bfg.apps.notifications.factories import NotificationFactory
from social_bfg.apps.notifications.models import Notification
from social_bfg.apps.posts.factories import PostFactory
from social_bfg.apps.private_messages.factories import MessageFactory

# Local
from ..factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserPreviewView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        response = client.get(reverse("users:preview", args=[user.username]))
        assert response.status_code == 200


class TestMemberListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        response = client.get(reverse("users:member_list"))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert user in object_list
        assert member.member in object_list


class TestActivityLikesView:
    def test_get(self, client, member, transactional_db):
        owner = MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        )
        post = PostFactory(community=owner.community, owner=owner.member)
        LikeFactory(
            content_object=post, community=post.community, recipient=post.owner,
        )
        response = client.get(reverse("users:activity_likes", args=["danjac"]))
        assert response.status_code == 200
        assert response.context["object_list"][0]["object"] == post
        assert response.context["num_likes"] == 1


class TestActivityMentionsView:
    def test_get_if_own_mention(self, client, member, transactional_db):
        PostFactory(
            community=member.community,
            owner=member.member,
            mentions=f"@{member.member.username}",
        )
        response = client.get(
            reverse("users:activity_mentions", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0

    def test_get(self, client, member, transactional_db):
        MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        )
        post = PostFactory(
            community=member.community, owner=member.member, mentions="@danjac @tester",
        )
        response = client.get(reverse("users:activity_mentions", args=["danjac"]))
        assert response.status_code == 200
        assert response.context["object_list"][0]["object"] == post


class TestCommentLikesView:
    def test_get(self, client, member, transactional_db):
        owner = MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        )
        comment = CommentFactory(community=owner.community, owner=owner.member,)
        LikeFactory(
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        response = client.get(reverse("users:comment_likes", args=["danjac"]))
        assert response.status_code == 200
        assert response.context["object_list"][0] == comment
        assert response.context["num_likes"] == 1


class TestCommentMentionsView:
    def test_get_if_own_mention(self, client, member, transactional_db):
        CommentFactory(
            community=member.community,
            owner=member.member,
            content=f"@{member.member.username}",
        )
        response = client.get(
            reverse("users:comment_mentions", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0

    def test_get(self, client, member, transactional_db):
        MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        )
        comment = CommentFactory(
            community=member.community, owner=member.member, content="@danjac @tester",
        )
        response = client.get(reverse("users:comment_mentions", args=["danjac"]))
        assert response.status_code == 200
        assert response.context["object_list"][0] == comment


class TestFollowingUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.following.add(user)
        response = client.get(reverse("users:following_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestBlockedUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.blocked.add(user)
        response = client.get(reverse("users:blocked_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestFollowerUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        user.following.add(member.member)
        response = client.get(reverse("users:follower_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestUserCommentsView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, owner=member.member, community=member.community,
        )
        LikeFactory(
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        response = client.get(reverse("users:comments", args=[comment.owner.username]))
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 1
        assert dict(response.context or {})["num_likes"] == 1


class TestUserActivitiesView:
    def test_if_anonymous(self, client, community):
        response = client.get(reverse("users:activities", args=["testuser"]))
        assert response.url.startswith(reverse(settings.LOGIN_URL))

    def test_if_not_found(self, client, member):
        response = client.get(reverse("users:activities", args=["testuser"]))
        assert response.status_code == 404
        assertTemplateUsed(response, "users/detail/not_found.html")

    def test_get_if_current_user(self, client, member):

        post = PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)
        # unlikely, but just for testing
        notification = NotificationFactory(
            recipient=member.member, content_object=member.member, is_read=False,
        )
        LikeFactory(
            content_object=post, community=post.community, recipient=post.owner,
        )

        response = client.get(
            reverse("users:activities", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 2
        assert dict(response.context or {})["num_likes"] == 1

        # ignore: user is self
        notification.refresh_from_db()
        assert not notification.is_read

    def test_get_if_other_user(self, client, member):

        other = MembershipFactory(community=member.community)
        post = PostFactory(community=member.community, owner=other.member)
        EventFactory(community=member.community, owner=other.member)
        notification = NotificationFactory(
            recipient=member.member, content_object=other.member, is_read=False
        )
        LikeFactory(
            content_object=post, community=post.community, recipient=post.owner,
        )

        response = client.get(reverse("users:activities", args=[other.member.username]))
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 2
        assert dict(response.context or {})["num_likes"] == 1

        notification.refresh_from_db()
        assert notification.is_read

    def test_get_if_other_user_email_same_as_username(self, client, member):
        """
        Test for regex
        """
        other = MembershipFactory(
            community=member.community, member=UserFactory(username="tester@gmail.com"),
        )
        response = client.get(reverse("users:activities", args=[other.member.username]))
        assert response.status_code == 200


class TestUserUpdateView:
    def test_get(self, client, login_user):
        response = client.get(reverse("user_update"))
        assert response.status_code == 200

    def test_post(self, client, login_user):
        response = client.post(
            reverse("user_update"),
            {"name": "New Name", "language": "en", "default_timezone": "UTC"},
        )
        assert response.url == reverse("user_update")
        login_user.refresh_from_db()
        assert login_user.name == "New Name"


class TestUserDeleteView:
    def test_get(self, client, login_user):
        response = client.get(reverse("user_delete"))
        assert response.status_code == 200

    def test_post(self, client, user_model, login_user):
        response = client.post(reverse("user_delete"))
        assert response.url == "/"
        assert user_model.objects.filter(username=login_user.username).count() == 0


class TestUserFollowView:
    def test_post(self, client, member, mailoutbox, send_webpush_mock):
        user = MembershipFactory(
            community=member.community, member=UserFactory(),
        ).member
        response = client.post(reverse("users:follow", args=[user.username]))
        assert response.status_code == 200
        assert user in member.member.following.all()
        notification = Notification.objects.get()
        assert notification.recipient == user
        assert notification.content_object == member.member
        assert notification.actor == member.member
        assert mailoutbox[0].to == [user.email]

    def test_post_user_blocked(self, client, member):
        user = MembershipFactory(
            community=member.community, member=UserFactory(),
        ).member
        user.blockers.add(member.member)
        response = client.post(reverse("users:follow", args=[user.username]))
        assert response.status_code == 404
        assert user not in member.member.following.all()

    def test_post_user_blocking(self, client, member):
        user = MembershipFactory(
            community=member.community, member=UserFactory(),
        ).member
        member.member.blockers.add(user)
        response = client.post(reverse("users:follow", args=[user.username]))
        assert response.status_code == 404
        assert user not in member.member.following.all()


class TestUserUnfollowView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.following.add(user)
        response = client.post(reverse("users:unfollow", args=[user.username]))
        assert response.status_code == 200
        assert user not in member.member.following.all()


class TestUserBlockView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        response = client.post(reverse("users:block", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user in member.member.blocked.all()


class TestUserUnblockView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.blocked.add(user)
        response = client.post(reverse("users:unblock", args=[user.username]))
        assert user not in member.member.blocked.all()
        assert response.url == user.get_absolute_url()


class TestUserAutocompleteListView:
    def test_get(self, client, member, user):
        other = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member

        blocker = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member

        blocker.blocked.add(member.member)

        response = client.get(reverse("users:autocomplete_list"), {"q": "tester"})
        object_list = response.context["object_list"]
        assert other in object_list
        assert blocker not in object_list


class TestUserMessageListView:
    def test_get_if_other(self, client, member):
        other_user = MembershipFactory(community=member.community).member
        from_me = MessageFactory(
            community=member.community, sender=member.member, recipient=other_user,
        )
        to_me = MessageFactory(
            community=member.community, sender=other_user, recipient=member.member,
        )
        to_someone_else = MessageFactory(community=member.community, sender=other_user)
        response = client.get(reverse("users:messages", args=[other_user.username]))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert from_me in object_list
        assert to_me in object_list
        assert to_someone_else not in object_list

    def test_get_if_current_user(self, client, member):
        other_user = MembershipFactory(community=member.community).member
        from_me = MessageFactory(
            community=member.community, sender=member.member, recipient=other_user,
        )
        to_me = MessageFactory(
            community=member.community, sender=other_user, recipient=member.member,
        )
        to_someone_else = MessageFactory(community=member.community, sender=other_user)
        response = client.get(reverse("users:messages", args=[member.member.username]))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert from_me in object_list
        assert to_me in object_list
        assert to_someone_else not in object_list


class TestDismissNoticeView:
    def test_post(self, client, login_user):
        response = client.post(reverse("dismiss_notice", args=["private-stash"]))
        assert response.status_code == 200
        login_user.refresh_from_db()
