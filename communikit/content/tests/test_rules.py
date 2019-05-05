import pytest

from django.conf import settings

from communikit.communities.models import Community, Membership
from communikit.content.models import Post
from communikit.content.rules import (
    is_author,
    is_editor,
    is_post_community_moderator,
)
from communikit.content.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestIsAuthor:
    def test_is_author(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory(author=user)
        assert is_author.test(user, post)
        assert is_editor.test(user, post)

    def test_is_not_author(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory()
        assert not is_author.test(user, post)
        assert not is_editor.test(user, post)


class TestIsPostCommunityModerator:
    def test_is_moderator(self, moderator: settings.AUTH_USER_MODEL):
        post = PostFactory(community=moderator.community)
        assert is_post_community_moderator.test(moderator.member, post)
        assert is_editor(moderator.member, post)

    def test_is_not_moderator(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory()
        assert not is_post_community_moderator.test(user, post)
        assert not is_editor(user, post)


class TestPermissions:
    def test_author_can_like_post(self, post: Post):
        assert not post.author.has_perm("content.like_post", post)

    def test_member_can_like_post(self, member: Membership):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("content.like_post", post)

    def test_member_can_create_post(self, member: Membership):
        assert member.member.has_perm("content.create_post", member.community)

    def test_non_member_can_create_post(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not user.has_perm("content.create_post", community)

    def test_author_can_edit_or_delete_post(
        self, user: settings.AUTH_USER_MODEL
    ):
        post = PostFactory(author=user)
        assert user.has_perm("content.change_post", post)
        assert user.has_perm("content.delete_post", post)

    def test_non_author_can_edit_or_delete_post(
        self, user: settings.AUTH_USER_MODEL
    ):
        post = PostFactory()
        assert not user.has_perm("content.change_post", post)
        assert not user.has_perm("content.delete_post", post)

    def test_moderator_can_edit_or_delete_post(
        self, moderator: settings.AUTH_USER_MODEL
    ):
        post = PostFactory(community=moderator.community)

        assert moderator.member.has_perm("content.change_post", post)
        assert moderator.member.has_perm("content.delete_post", post)
