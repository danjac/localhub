# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.utils import timezone

from ..factories import CommentFactory
from ..rules import (
    is_comment_community_moderator,
    is_deleted,
    is_owner,
    is_content_object_deleted,
)

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_is_owner(self, comment):
        assert is_owner.test(comment.owner, comment)

    def test_is_not_owner(self, comment, user):
        assert not is_owner.test(user, comment)


class TestIsDeleted:
    def test_is_not_deleted(self, comment):
        assert not is_deleted.test(comment.owner, comment)

    def test_is_deleted(self, comment):
        comment.deleted = timezone.now()
        assert is_deleted.test(comment.owner, comment)


class TestIsContentObjectDeleted:
    def test_is_not_deleted(self, comment):
        assert not is_content_object_deleted.test(comment.owner, comment)

    def test_is_deleted(self, comment):
        comment.content_object = None
        assert is_content_object_deleted.test(comment.owner, comment)

    def test_is_soft_deleted(self, comment):
        comment.content_object.deleted = timezone.now()
        assert is_content_object_deleted.test(comment.owner, comment)


class TestIsCommentCommunityModerator:
    def test_is_moderator(self, comment, moderator):
        assert is_comment_community_moderator.test(moderator.member, comment)

    def test_is_not_moderator(self, comment, user):
        assert not is_comment_community_moderator.test(user, comment)

    def test_is_moderator_of_different_community(self, community, moderator):
        assert not is_comment_community_moderator.test(
            moderator.member, CommentFactory()
        )


class TestBookmarkPermissions:
    def test_can_bookmark_comment_if_member(self, comment, member):
        assert member.member.has_perm("comments.bookmark_comment", comment)

    def test_can_bookmark_comment_if_member_deleted(self, comment, member):
        comment.deleted = timezone.now()
        assert not member.member.has_perm("comments.bookmark_comment", comment)

    def test_can_bookmark_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.bookmark_comment", comment)


class TestLikePermissions:
    def test_can_like_comment_if_owner(self, comment):
        assert not comment.owner.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_member(self, comment, member):
        assert member.member.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_member_deleted(self, comment, member):
        comment.deleted = timezone.now()
        assert not member.member.has_perm("comments.like_comment", comment)

    def test_can_like_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.like_comment", comment)


class TestFlagPermissions:
    def test_can_flag_comment_if_owner(self, comment):
        assert not comment.owner.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_member(self, comment, member):
        assert member.member.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_member_deleted(self, comment, member):
        comment.deleted = timezone.now()
        assert not member.member.has_perm("comments.flag_comment", comment)

    def test_can_flag_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.flag_comment", comment)


class TestReplyPermissions:
    def test_can_reply_to_comment_if_member(self, comment, member):
        assert member.member.has_perm("comments.reply_to_comment", comment)

    def test_can_reply_to_comment_if_member_deleted(self, comment, member):
        comment.deleted = timezone.now()
        assert not member.member.has_perm("comments.reply_to_comment", comment)

    def test_can_reply_to_comment_if_not_member(self, comment, user):
        assert not user.has_perm("comments.reply_to_comment", comment)

    def test_can_reply_to_comment_if_content_object_deleted(self, comment, member):
        comment.content_object = None
        assert not member.member.has_perm("comments.reply_to_comment", comment)


class TestChangePermissions:
    def test_can_change_comment_if_owner(self, comment):
        assert comment.owner.has_perm("comments.change_comment", comment)

    def test_can_change_comment_if_owner_deleted(self, comment):
        comment.deleted = timezone.now()
        assert not comment.owner.has_perm("comments.change_comment", comment)

    def test_can_change_comment_if_not_owner(self, comment, user):
        assert not user.has_perm("comments.change_comment", comment)


class TestDeletePermissions:
    def test_can_delete_comment_if_owner(self, comment):
        assert comment.owner.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_owner_deleted(self, comment):
        comment.deleted = timezone.now()
        assert comment.owner.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_not_owner(self, comment, user):
        assert not user.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_moderator(self, comment, moderator):
        assert moderator.member.has_perm("comments.delete_comment", comment)

    def test_can_delete_comment_if_moderator_deleted(self, comment, moderator):
        comment.deleted = timezone.now()
        assert not moderator.member.has_perm("comments.delete_comment", comment)
