import factory
import pytest

from django.db.models import signals
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Community, Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCommentManager:
    def test_search(self):

        comment = CommentFactory(content="testme")
        other_comment = CommentFactory(content="not found")

        comment.search_indexer.update()
        other_comment.search_indexer.update()

        assert Comment.objects.search("testme").get() == comment

    def test_blocked_users(self, user: settings.AUTH_USER_MODEL):

        my_comment = CommentFactory(owner=user)

        first_comment = CommentFactory()
        second_comment = CommentFactory()
        user.blocked.add(first_comment.owner)

        comments = Comment.objects.blocked_users(user).all()
        assert len(comments) == 2
        assert my_comment in comments
        assert second_comment in comments

    def test_For_community(self, community: Community):
        comment = CommentFactory(
            community=community,
            owner=MembershipFactory(community=community).member,
        )
        CommentFactory(owner=MembershipFactory(community=community).member)
        CommentFactory(community=community)
        CommentFactory()
        assert Comment.objects.for_community(community).get() == comment

    def test_with_num_likes(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )

        comment = Comment.objects.with_num_likes().get()
        assert comment.num_likes == 1

    def test_with_has_flagged_if_user_has_not_flagged(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(UserFactory()).get()
        assert not comment.has_flagged

    def test_with_has_flagged_if_user_has_flagged(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(user).get()
        assert comment.has_flagged

    def test_with_has_liked_if_user_has_not_liked(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(UserFactory()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_liked(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(user).get()
        assert comment.has_liked

    def test_with_common_annotations_if_anonymous(self, comment: Comment):
        comment = Comment.objects.with_common_annotations(
            comment.community, AnonymousUser()
        ).get()

        assert not hasattr(comment, "num_likes")
        assert not hasattr(comment, "has_liked")
        assert not hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")

    def test_with_common_annotations_if_authenticated(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        comment = Comment.objects.with_common_annotations(
            comment.community, user
        ).get()

        assert hasattr(comment, "num_likes")
        assert hasattr(comment, "has_liked")
        assert hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")


class TestCommentModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, community: Community):
        comment_owner = UserFactory(username="comment_owner")
        post_owner = UserFactory(username="post_owner")
        moderator = UserFactory()

        Membership.objects.create(
            member=comment_owner,
            community=community,
            role=Membership.ROLES.moderator,
        )

        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )
        mentioned = UserFactory(username="danjac")

        Membership.objects.create(
            member=mentioned, community=community, role=Membership.ROLES.member
        )

        post = PostFactory(owner=post_owner, community=community)

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        notifications = comment.notify(created=True)

        assert len(notifications) == 3

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == moderator
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "moderator_review_request"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "new_comment"

        # edit by moderator
        comment.editor = moderator
        comment.save()

        notifications = comment.notify(created=False)
        assert len(notifications) == 1

        assert notifications[0].recipient == comment.owner
        assert notifications[0].actor == moderator
        assert notifications[0].verb == "moderator_edit"
