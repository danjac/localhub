import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text

from communikit.comments.models import Comment
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Community, Membership
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestCommentCreateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.get(reverse("comments:create", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("comments:create", args=[post.id]), {"content": "test"}
        )
        assert response.url == post.get_absolute_url()
        comment = post.comment_set.get()
        assert comment.owner == member.member
