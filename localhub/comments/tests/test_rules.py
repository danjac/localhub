import pytest

from django.conf import settings


from localhub.communities.models import Membership, Community
from localhub.comments.models import Comment
from localhub.comments.rules import is_owner, is_comment_community_moderator
from localhub.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_is_owner(self, comment: Comment):
        assert is_owner.test(comment.owner, comment)

    def test_is_not_owner(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not is_owner.test(user, comment)


class TestIsCommentCommunityModerator:
    def test_is_moderator(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(
            member=user, community=comment.community, role="moderator"
        )
        assert is_comment_community_moderator.test(user, comment)

    def test_is_not_moderator(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not is_comment_community_moderator.test(user, comment)

    def test_is_moderator_of_different_community(
        self,
        comment: Comment,
        user: settings.AUTH_USER_MODEL,
        community: Community,
    ):
        Membership.objects.create(
            member=user, community=community, role="moderator"
        )
        assert not is_comment_community_moderator.test(user, comment)


class TestPermissions:
    def test_can_like_comment_if_owner(self, comment: Comment):
        assert not comment.owner.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_member(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(member=user, community=comment.community)
        assert user.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_not_member(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not user.has_perm("comments.like_comment", comment)

    def test_can_flag_comment_if_owner(self, comment: Comment):
        assert not comment.owner.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_member(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(member=user, community=comment.community)
        assert user.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_not_member(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not user.has_perm("comments.flag_comment", comment)

    def test_can_change_comment_if_owner(self, comment: Comment):
        assert comment.owner.has_perm("comments.change_comment", comment)

    def test_can_change_comment_if_not_owner(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not user.has_perm("comments.change_comment", comment)

    def test_can_delete_comment_if_owner(self, comment: Comment):
        assert comment.owner.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_not_owner(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        assert not user.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_moderator(
        self, comment: Comment, user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(
            member=user, community=comment.community, role="moderator"
        )
        assert user.has_perm("comments.delete_comment", comment)
