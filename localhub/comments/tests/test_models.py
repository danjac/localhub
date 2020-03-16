# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

from ..factories import CommentFactory
from ..models import Comment

pytestmark = pytest.mark.django_db


class TestCommentManager:
    @pytest.mark.django_db(transaction=True)
    def test_search(self):

        comment = CommentFactory(content="testme")
        CommentFactory(content="not found")

        assert Comment.objects.search("testme").get() == comment

    def test_exclude_blocked_users(self, user):

        my_comment = CommentFactory(owner=user)

        first_comment = CommentFactory()
        second_comment = CommentFactory()
        user.blocked.add(first_comment.owner)

        comments = Comment.objects.exclude_blocked_users(user).all()
        assert len(comments) == 2
        assert my_comment in comments
        assert second_comment in comments

    def test_with_is_blocked_if_anonymous(self):

        CommentFactory()
        assert not Comment.objects.with_is_blocked(AnonymousUser()).get().is_blocked

    def test_with_is_blocked_if_not_blocked(self, user):

        CommentFactory()

        assert not Comment.objects.with_is_blocked(user).get().is_blocked

    def test_with_is_blocked_if_blocked(self, user):

        my_comment = CommentFactory()
        user.blocked.add(my_comment.owner)

        assert Comment.objects.with_is_blocked(user).get().is_blocked

    def test_with_is_parent_owner_member_true(self, community):
        parent = CommentFactory(
            community=community, owner=MembershipFactory(community=community).member,
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
            community=community, owner=MembershipFactory(community=community).member,
        )
        CommentFactory(owner=MembershipFactory(community=community).member)
        CommentFactory(community=community)
        CommentFactory()
        assert Comment.objects.for_community(community).get() == comment

    def test_with_num_likes(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )

        comment = Comment.objects.with_num_likes().get()
        assert comment.num_likes == 1

    def test_with_has_flagged_if_user_has_not_flagged(self, comment, user):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(UserFactory()).get()
        assert not comment.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, comment, user):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(user).get()
        assert comment.has_flagged

    def test_with_has_liked_if_user_has_not_liked(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(UserFactory()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_liked(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(user).get()
        assert comment.has_liked

    def test_with_common_annotations_if_anonymous(self, comment):
        comment = Comment.objects.with_common_annotations(
            AnonymousUser(), comment.community
        ).get()

        assert not hasattr(comment, "num_likes")
        assert not hasattr(comment, "has_liked")
        assert not hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")

    def test_with_common_annotations_if_authenticated(self, comment, user):
        comment = Comment.objects.with_common_annotations(user, comment.community).get()

        assert hasattr(comment, "num_likes")
        assert hasattr(comment, "has_liked")
        assert hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")


class TestCommentModel:
    def test_abbreviate(self):
        comment = Comment(content="Hello\nthis is a *test*")
        assert comment.abbreviate() == "Hello this is a test"

    def test_notify_on_create(self, community):

        comment_owner = MembershipFactory(community=community).member
        post_owner = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(owner=post_owner, community=community)

        other_comment = CommentFactory(
            owner=MembershipFactory(community=community, member=UserFactory(),).member,
            content_object=post,
        )

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        follower = MembershipFactory(community=community, member=UserFactory(),).member
        follower.following.add(comment.owner)

        notifications = list(comment.notify_on_create())

        assert len(notifications) == 5

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == moderator
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "moderator_review"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "new_comment"

        assert notifications[3].recipient == other_comment.owner
        assert notifications[3].actor == comment.owner
        assert notifications[3].verb == "new_sibling"

        assert notifications[4].recipient == follower
        assert notifications[4].actor == comment.owner
        assert notifications[4].verb == "followed_user"

    def test_notify_on_create_if_parent(self, community):

        comment_owner = MembershipFactory(community=community,).member

        parent_owner = MembershipFactory(
            community=community, member=UserFactory(),
        ).member

        post_owner = MembershipFactory(
            community=community, member=UserFactory(),
        ).member

        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(owner=post_owner, community=community)

        other_comment = CommentFactory(
            owner=MembershipFactory(community=community, member=UserFactory(),).member,
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

        follower = MembershipFactory(community=community, member=UserFactory(),).member
        follower.following.add(comment.owner)

        notifications = list(comment.notify_on_create())

        assert len(notifications) == 6

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == moderator
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "moderator_review"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "new_comment"

        assert notifications[3].recipient == parent_owner
        assert notifications[3].actor == comment.owner
        assert notifications[3].verb == "reply"

        assert notifications[4].recipient == other_comment.owner
        assert notifications[4].actor == comment.owner
        assert notifications[4].verb == "new_sibling"

        assert notifications[5].recipient == follower
        assert notifications[5].actor == comment.owner
        assert notifications[5].verb == "followed_user"

    def test_notify_on_update(self, community):

        comment_owner = MembershipFactory(
            community=community, member=UserFactory(),
        ).member

        post_owner = MembershipFactory(community=community).member
        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator, member=UserFactory(),
        ).member

        post = PostFactory(owner=post_owner, community=community)

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        # edit by owner
        comment.content = "edit #2"
        comment.editor = comment_owner
        comment.save()

        notifications = list(comment.notify_on_update())
        assert len(notifications) == 1

        assert notifications[0].recipient == moderator
        assert notifications[0].actor == comment_owner
        assert notifications[0].verb == "moderator_review"
