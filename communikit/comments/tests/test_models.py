import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.comments.models import Comment
from communikit.flags.models import Flag
from communikit.likes.models import Like
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCommentManager:
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
