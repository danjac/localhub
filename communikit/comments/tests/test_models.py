import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.comments.models import Comment, Like
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCommentManager:
    def test_with_num_likes(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, comment=comment)

        comment = Comment.objects.with_num_likes().get()
        assert comment.num_likes == 1

    def test_with_has_liked_if_user_anonymous(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, comment=comment)
        comment = Comment.objects.with_has_liked(AnonymousUser()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_not_liked(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, comment=comment)
        comment = Comment.objects.with_has_liked(UserFactory()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_liked(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, comment=comment)
        comment = Comment.objects.with_has_liked(user).get()
        assert comment.has_liked
