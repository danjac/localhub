# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone

# Third Party Libraries
import pytest

# Localhub
from localhub.activities.posts.factories import PostFactory
from localhub.bookmarks.factories import BookmarkFactory
from localhub.communities.factories import MembershipFactory
from localhub.flags.factories import FlagFactory
from localhub.likes.factories import LikeFactory
from localhub.notifications.factories import NotificationFactory
from localhub.users.factories import UserFactory

# Local
from ..factories import CommentFactory
from ..models import Comment

pytestmark = pytest.mark.django_db


class TestCommentManager:
    @pytest.mark.django_db(transaction=True)
    def test_search(self):

        comment = CommentFactory(content="testme")
        CommentFactory(content="not found")

        assert Comment.objects.search("testme").get() == comment

    def test_remove_content_objects(self, comment):

        Comment.objects.remove_content_objects()
        comment.refresh_from_db()
        assert comment.object_id is None
        assert comment.content_type is None
        assert comment.content_object is None

    def test_deleted_if_deleted(self):

        CommentFactory(deleted=timezone.now())
        assert Comment.objects.deleted().count() == 1

    def test_deleted_if_not_deleted(self):

        CommentFactory(deleted=None)
        assert Comment.objects.deleted().count() == 0

    def test_exclude_deleted_if_deleted(self, user):

        comment = CommentFactory(deleted=timezone.now())
        assert Comment.objects.exclude_deleted().count() == 0
        assert Comment.objects.exclude_deleted(user).count() == 0
        assert Comment.objects.exclude_deleted(comment.owner).count() == 1

    def test_exclude_deleted_if_not_deleted(self, user):

        comment = CommentFactory(deleted=None)
        assert Comment.objects.exclude_deleted().count() == 1
        assert Comment.objects.exclude_deleted(user).count() == 1
        assert Comment.objects.exclude_deleted(comment.owner).count() == 1

    def test_exclude_blocked_users(self, user):

        my_comment = CommentFactory(owner=user)

        first_comment = CommentFactory()
        second_comment = CommentFactory()
        user.blocked.add(first_comment.owner)

        comments = Comment.objects.exclude_blocked_users(user).all()
        assert len(comments) == 2
        assert my_comment in comments
        assert second_comment in comments

    def test_exclude_blocking_users(self, user):

        my_comment = CommentFactory(owner=user)

        first_comment = CommentFactory()
        second_comment = CommentFactory()
        user.blockers.add(first_comment.owner)

        comments = Comment.objects.exclude_blocked_users(user).all()
        assert len(comments) == 2
        assert my_comment in comments
        assert second_comment in comments

    def test_with_is_blocked_if_anonymous(self, anonymous_user):

        CommentFactory()
        assert not Comment.objects.with_is_blocked(anonymous_user).get().is_blocked

    def test_with_is_blocked_if_not_blocked(self, user):

        CommentFactory()

        assert not Comment.objects.with_is_blocked(user).get().is_blocked

    def test_with_is_blocked_if_blocked(self, user):

        my_comment = CommentFactory()
        user.blocked.add(my_comment.owner)

        assert Comment.objects.with_is_blocked(user).get().is_blocked

    def test_with_is_parent_owner_member_true(self, community):
        parent = CommentFactory(
            community=community,
            owner=MembershipFactory(community=community).member,
        )

        comment = CommentFactory(
            community=community,
            parent=parent,
            owner=MembershipFactory(community=community).member,
        )

        assert (
            Comment.objects.with_is_parent_owner_member(community)
            .for_community(community)
            .get(pk=comment.id)
            .is_parent_owner_member
        )

    def test_with_is_parent_owner_member_false(self, community):
        parent = CommentFactory(community=community)

        comment = CommentFactory(
            community=community,
            parent=parent,
            owner=MembershipFactory(community=community).member,
        )

        assert (
            not Comment.objects.with_is_parent_owner_member(community)
            .for_community(community)
            .get(pk=comment.id)
            .is_parent_owner_member
        )

    def test_for_community(self, community):
        comment = CommentFactory(
            community=community,
            owner=MembershipFactory(community=community).member,
        )
        CommentFactory(owner=MembershipFactory(community=community).member)
        CommentFactory(community=community)
        CommentFactory()
        assert Comment.objects.for_community(community).get() == comment

    def test_with_num_likes(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )

        comment = Comment.objects.with_num_likes().get()
        assert comment.num_likes == 1

    def test_with_has_flagged_if_user_has_not_flagged(self, comment, user):
        FlagFactory(user=user, content_object=comment, community=comment.community)
        comment = Comment.objects.with_has_flagged(UserFactory()).get()
        assert not comment.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, comment, user):
        FlagFactory(user=user, content_object=comment, community=comment.community)
        comment = Comment.objects.with_has_flagged(user).get()
        assert comment.has_flagged

    def test_with_has_bookmarked_if_user_has_not_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        comment = Comment.objects.with_has_bookmarked(UserFactory()).get()
        assert not comment.has_bookmarked

    def test_with_has_bookmarked_if_user_has_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        comment = Comment.objects.with_has_bookmarked(user).get()
        assert comment.has_bookmarked

    def test_bookmarked_if_user_has_not_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        assert Comment.objects.bookmarked(UserFactory()).count() == 0

    def test_bookmarked_if_user_has_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        comments = Comment.objects.bookmarked(user)
        assert comments.count() == 1
        assert comments.first().has_bookmarked

    def test_with_bookmarked_timestamp_if_user_has_not_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        # test with *another* user
        comment = Comment.objects.with_bookmarked_timestamp(UserFactory()).first()
        assert comment.bookmarked is None

    def test_with_bookmarked_timestamp_if_user_has_bookmarked(self, comment, user):
        BookmarkFactory(
            user=user,
            content_object=comment,
            community=comment.community,
        )
        comment = Comment.objects.with_bookmarked_timestamp(user).first()
        assert comment.bookmarked is not None

    def test_with_has_liked_if_user_has_not_liked(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(UserFactory()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_liked(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(user).get()
        assert comment.has_liked

    def test_liked_if_user_has_not_liked(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        assert Comment.objects.liked(UserFactory()).count() == 0

    def test_liked_if_user_has_liked(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comments = Comment.objects.liked(user)
        assert comments.count() == 1
        assert comments.first().has_liked

    def test_with_liked_timestamp_if_user_has_liked(self, comment, user):
        LikeFactory(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_liked_timestamp(user).first()
        assert comment.liked is not None

    def test_with_liked_timestamp_if_user_has_not_liked(self, comment, user):
        comment = Comment.objects.with_liked_timestamp(user).first()
        assert comment.liked is None

    def test_with_common_annotations_if_anonymous(self, comment, anonymous_user):
        comment = Comment.objects.with_common_annotations(
            anonymous_user, comment.community
        ).get()

        assert comment.num_likes is None
        assert not comment.has_liked
        assert not comment.has_flagged
        assert not comment.is_new
        assert not hasattr(comment, "is_flagged")

    def test_with_common_annotations_if_authenticated(self, comment, user):
        comment = Comment.objects.with_common_annotations(user, comment.community).get()

        assert hasattr(comment, "is_new")
        assert hasattr(comment, "num_likes")
        assert hasattr(comment, "has_liked")
        assert hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")

    def test_with_common_annotations_if_moderator(self, comment, moderator):
        comment = Comment.objects.with_common_annotations(
            moderator.member, comment.community
        ).get()

        assert hasattr(comment, "is_new")
        assert hasattr(comment, "num_likes")
        assert hasattr(comment, "has_liked")
        assert hasattr(comment, "has_flagged")
        assert hasattr(comment, "is_flagged")

    def test_with_is_new_if_notification_is_unread(self, comment, member):
        NotificationFactory(
            verb="mention",
            recipient=member.member,
            content_object=comment,
            is_read=False,
        )

        comments = Comment.objects.with_is_new(member.member)
        first = comments.first()
        assert first.is_new

    def test_with_is_new_if_notification_is_unread_anon(
        self, comment, member, anonymous_user
    ):
        NotificationFactory(
            verb="mention",
            recipient=member.member,
            content_object=comment,
            is_read=False,
        )

        comments = Comment.objects.with_is_new(anonymous_user)
        first = comments.first()
        assert not first.is_new

    def test_with_is_new_if_notification_is_read(self, comment, member):
        NotificationFactory(
            verb="mention",
            recipient=member.member,
            content_object=comment,
            is_read=True,
        )

        comments = Comment.objects.with_is_new(member.member)
        first = comments.first()
        assert not first.is_new

    def test_with_is_new_if_notification_is_unread_wrong_recipient(
        self, comment, member
    ):
        NotificationFactory(verb="mention", content_object=comment, is_read=False)

        comments = Comment.objects.with_is_new(member.member)
        first = comments.first()
        assert not first.is_new


class TestCommentModel:
    def test_abbreviate(self):
        comment = Comment(content="Hello\nthis is a *test*")
        assert comment.abbreviate() == "Hello this is a test"

    def test_soft_delete(self, comment):
        NotificationFactory(content_object=comment)
        LikeFactory(content_object=comment)
        comment.soft_delete()
        assert comment.deleted is not None
        assert comment.get_notifications().count() == 0
        assert comment.get_likes().count() == 0

    def test_notify_on_create_if_no_content_object(self, community):

        comment_owner = MembershipFactory(community=community).member
        post_owner = MembershipFactory(
            community=community,
        ).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(
            owner=post_owner, community=community, deleted=timezone.now()
        )

        CommentFactory(
            owner=MembershipFactory(community=community).member,
            content_object=post,
        )

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        follower = MembershipFactory(community=community).member
        follower.following.add(comment.owner)

        notifications = list(comment.notify_on_create())

        assert len(notifications) == 0

    def test_notify_on_create(self, community, mailoutbox, send_webpush_mock):

        comment_owner = MembershipFactory(community=community).member
        post_owner = MembershipFactory(
            community=community,
        ).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(owner=post_owner, community=community)

        other_comment = CommentFactory(
            owner=MembershipFactory(community=community).member,
            content_object=post,
        )

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        follower = MembershipFactory(community=community).member
        follower.following.add(comment.owner)

        notifications = list(comment.notify_on_create())

        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == post.owner
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "new_comment"

        assert notifications[2].recipient == other_comment.owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "new_sibling"

        assert notifications[3].recipient == follower
        assert notifications[3].actor == comment.owner
        assert notifications[3].verb == "followed_user"

    def test_notify_on_create_if_parent(self, community, mailoutbox, send_webpush_mock):

        comment_owner = MembershipFactory(
            community=community,
        ).member

        parent_owner = MembershipFactory(community=community).member

        post_owner = MembershipFactory(community=community).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(owner=post_owner, community=community)

        other_comment = CommentFactory(
            owner=MembershipFactory(community=community).member,
            content_object=post,
        )

        parent = CommentFactory(
            owner=parent_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        comment = CommentFactory(
            owner=comment_owner,
            parent=parent,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        follower = MembershipFactory(community=community).member
        follower.following.add(comment.owner)

        notifications = list(comment.notify_on_create())

        assert len(notifications) == 5

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == post.owner
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "new_comment"

        assert notifications[2].recipient == parent_owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "reply"

        assert notifications[3].recipient == other_comment.owner
        assert notifications[3].actor == comment.owner
        assert notifications[3].verb == "new_sibling"

        assert notifications[4].recipient == follower
        assert notifications[4].actor == comment.owner
        assert notifications[4].verb == "followed_user"

    def test_notify_on_update(self, community, mailoutbox, send_webpush_mock):

        comment_owner = MembershipFactory(
            community=community,
        ).member

        member = MembershipFactory(
            community=community, member=UserFactory(username="danjac")
        ).member

        post_owner = MembershipFactory(community=community).member
        post = PostFactory(owner=post_owner, community=community)

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello",
        )

        comment.content = "hello @danjac"
        comment.save()

        notifications = list(comment.notify_on_update())
        assert len(notifications) == 1

        assert notifications[0].recipient == member
        assert notifications[0].actor == comment_owner
        assert notifications[0].verb == "mention"

    def test_notify_on_delete(self, comment, moderator, send_webpush_mock):
        notifications = comment.notify_on_delete(moderator.member)
        assert len(notifications) == 1

        assert notifications[0].actor == moderator.member
        assert notifications[0].recipient == comment.owner
        assert notifications[0].verb == "delete"

    def test_get_content_object(self, comment):
        assert comment.get_content_object() is not None

    def test_get_content_object_if_none(self):
        assert CommentFactory(content_object=None).get_content_object() is None

    def test_get_content_object_if_soft_deleted(self):
        assert (
            CommentFactory(
                content_object=PostFactory(deleted=timezone.now())
            ).get_content_object()
            is None
        )

    def test_get_parent_if_none(self, comment):
        assert comment.get_parent() is None

    def test_get_parent_if_exists(self, comment):
        assert CommentFactory(parent=comment).get_parent() == comment

    def test_get_parent_if_soft_deleted(self):
        assert (
            CommentFactory(parent=CommentFactory(deleted=timezone.now())).get_parent()
            is None
        )
