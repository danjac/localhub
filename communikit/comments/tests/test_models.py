import pytest

from django.conf import settings
from django.utils.encoding import force_str

from communikit.comments.models import Comment
from communikit.likes.models import Like

pytestmark = pytest.mark.django_db


class TestComments:
    def test_markdown(self):
        comment = Comment(content="*testing*")
        assert force_str(comment.markdown()) == "<p><em>testing</em></p>"

    def test_like(self, comment: Comment, user: settings.AUTH_USER_MODEL):
        assert comment.like(user)
        assert Like.objects.count() == 1

    def test_unlike(self, comment: Comment, user: settings.AUTH_USER_MODEL):
        Like.objects.create(content_object=comment, user=user)
        assert not comment.like(user)
        assert Like.objects.count() == 0
