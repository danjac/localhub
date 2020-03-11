# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.models import Membership

from ..factories import CommentFactory
from ..rules import is_comment_community_moderator, is_owner

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_is_owner(self, comment):
        assert is_owner.test(comment.owner, comment)

    def test_is_not_owner(self, comment, user):
        assert not is_owner.test(user, comment)


class TestIsCommentCommunityModerator:
    def test_is_moderator(self, comment, user):
        Membership.objects.create(
            member=user, community=comment.community, role="moderator"
        )
        assert is_comment_community_moderator.test(user, comment)

    def test_is_not_moderator(self, comment, user):
        assert not is_comment_community_moderator.test(user, comment)

    def test_is_moderator_of_different_community(self, user, community):
        Membership.objects.create(member=user, community=community, role="moderator")
        assert not is_comment_community_moderator.test(user, CommentFactory())


class TestLikePermissions:
    def test_can_like_comment_if_owner(self, comment):
        assert not comment.owner.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_member(self, comment, user):
        Membership.objects.create(member=user, community=comment.community)
        assert user.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.like_comment", comment)


class TestFlagPermissions:
    def test_can_flag_comment_if_owner(self, comment):
        assert not comment.owner.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_member(self, comment, user):
        Membership.objects.create(member=user, community=comment.community)
        assert user.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.flag_comment", comment)


class TestReplyPermissions:
    def test_can_reply_to_comment_if_member(self, comment, user):
        Membership.objects.create(member=user, community=comment.community)
        assert user.has_perm("comments.reply_to_comment", comment)

    def test_can_reply_to_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.reply_to_comment", comment)


class TestChangePermissions:
    def test_can_change_comment_if_owner(self, comment):
        assert comment.owner.has_perm("comments.change_comment", comment)

    def test_can_change_comment_if_not_owner(self, comment, user):
        assert not user.has_perm("comments.change_comment", comment)


class TestDeletePermissions:
    def test_can_delete_comment_if_owner(self, comment):
        assert comment.owner.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_not_owner(self, comment, user):
        assert not user.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_moderator(self, comment, user):
        Membership.objects.create(
            member=user, community=comment.community, role="moderator"
        )
        assert user.has_perm("comments.delete_comment", comment)
