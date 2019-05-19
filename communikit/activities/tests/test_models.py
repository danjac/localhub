import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.activities.models import Activity, Like
from communikit.comments.models import Comment
from communikit.posts.models import Post
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_with_num_comments(self, comment: Comment):
        activity = Activity.objects.with_num_comments().get()
        assert activity.num_comments == 1

    def test_with_num_likes(self, post: Post, user: settings.AUTH_USER_MODEL):
        Like.objects.create(user=user, activity=post)

        activity = Activity.objects.with_num_likes().get()
        assert activity.num_likes == 1

    def test_with_has_liked_if_user_anonymous(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, activity=post)
        activity = Activity.objects.with_has_liked(AnonymousUser()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_not_liked(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, activity=post)
        activity = Activity.objects.with_has_liked(UserFactory()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_liked(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, activity=post)
        activity = Activity.objects.with_has_liked(user).get()
        assert activity.has_liked

    def test_search(self):
        post = PostFactory(title="random thing")
        # normally fired when transaction commits
        post.make_search_updater()()
        result = Activity.objects.search("random thing").get()
        assert result.rank
