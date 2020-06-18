# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone

# Third Party Libraries
import pytest

# Localhub
from localhub.apps.communities.models import Community, Membership
from localhub.apps.posts.factories import PostFactory

# Local
from ..rules import is_activity_community_moderator, is_deleted, is_owner, is_published

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_is_owner(self, user):
        post = PostFactory(owner=user)
        assert is_owner.test(user, post)

    def test_is_not_owner(self, user):
        post = PostFactory()
        assert not is_owner.test(user, post)


class TestIsPublished:
    def test_is_published(self, user):
        post = PostFactory(owner=user, published=timezone.now())
        assert is_published.test(user, post)

    def test_is_not_published(self, user):
        post = PostFactory(owner=user, published=None)
        assert not is_published.test(user, post)


class TestIsDeleted:
    def test_is_deleted(self, user):
        post = PostFactory(owner=user, deleted=timezone.now())
        assert is_deleted.test(user, post)

    def test_is_not_deleted(self, user):
        post = PostFactory(owner=user, deleted=None)
        assert not is_deleted.test(user, post)


class TestIsPostCommunityModerator:
    def test_is_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        assert is_activity_community_moderator.test(moderator.member, post)

    def test_is_not_moderator(self, user):
        post = PostFactory()
        assert not is_activity_community_moderator.test(user, post)


class TestBookmarkPermissions:
    def test_member_can_bookmark_activity(self, member):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.bookmark_activity", post)

    def test_member_can_bookmark_activity_if_deleted(self, member):
        post = PostFactory(community=member.community, deleted=timezone.now())
        assert not member.member.has_perm("activities.bookmark_activity", post)

    def test_non_member_can_bookmark_activity(self, member):
        post = PostFactory()
        assert not member.member.has_perm("activities.bookmark_activity", post)

    def test_member_can_bookmark_activity_if_not_published(self, member):
        post = PostFactory(community=member.community, published=None)
        assert not member.member.has_perm("activities.bookmark_activity", post)


class TestLikePermissions:
    def test_owner_can_like_activity(self, post):
        assert not post.owner.has_perm("activities.like_activity", post)

    def test_member_can_like_activity(self, member):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.like_activity", post)

    def test_member_can_like_activity_if_not_published(self, member):
        post = PostFactory(community=member.community, published=None)
        assert not member.member.has_perm("activities.like_activity", post)


class TestPinPermissions:
    def test_member_can_pin_activity(self, member):
        post = PostFactory(community=member.community)
        assert not member.member.has_perm("activities.pin_activity", post)

    def test_moderator_can_pin_activity(self, moderator):
        post = PostFactory(community=moderator.community)
        assert moderator.member.has_perm("activities.pin_activity", post)

    def test_moderator_can_pin_activity_if_reshare(self, moderator):
        post = PostFactory(community=moderator.community, is_reshare=True)
        assert not moderator.member.has_perm("activities.pin_activity", post)

    def test_moderator_can_pin_activity_if_not_published(self, moderator):
        post = PostFactory(community=moderator.community, published=None)
        assert not moderator.member.has_perm("activities.pin_activity", post)


class TestResharePermissions:
    def test_owner_can_reshare_activity(self, post):
        assert not post.owner.has_perm("activities.reshare_activity", post)

    def test_parent_owner_can_reshare_activity(self, post):
        post = PostFactory(parent=PostFactory())
        assert not post.parent.owner.has_perm("activities.reshare_activity", post)

    def test_member_can_reshare_activity(self, member):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.reshare_activity", post)

    def test_member_can_reshare_activity_if_not_published(self, member):
        post = PostFactory(community=member.community, published=None)
        assert not member.member.has_perm("activities.reshare_activity", post)


class TestCreateCommentPermissions:
    def test_can_create_comment_if_member(self, post, user):
        Membership.objects.create(member=user, community=post.community)
        assert user.has_perm("activities.create_comment", post)

    def test_can_create_comment_if_member_if_not_published(self, member):
        post = PostFactory(community=member.community, published=None)
        assert not member.member.has_perm("activities.create_comment", post)

    def test_can_create_comment_if_does_not_allow_comments(self, post, user):
        post.allow_comments = False
        Membership.objects.create(member=user, community=post.community)
        assert not user.has_perm("activities.create_comment", post)

    def test_can_create_comment_if_not_member(self, post, user):
        assert not user.has_perm("activities.create_comment", post)


class TestFlagPermissions:
    def test_owner_can_flag_activity(self, post):
        assert not post.owner.has_perm("activities.flag_activity", post)

    def test_member_can_flag_activity(self, member):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.flag_activity", post)


class TestCreatePermissions:
    def test_member_can_create_activity(self, member):
        assert member.member.has_perm("activities.create_activity", member.community)

    def test_non_member_can_create_activity(self, user, community: Community):
        assert not user.has_perm("activities.create_activity", community)


class TestChangePermissions:
    def test_owner_can_change_activity(self, user):
        post = PostFactory(owner=user)
        assert user.has_perm("activities.change_activity", post)

    def test_owner_can_change_activity_if_deleted(self, user):
        post = PostFactory(owner=user, deleted=timezone.now())
        assert not user.has_perm("activities.change_activity", post)

    def test_owner_can_change_activity_if_reshare(self, user):
        post = PostFactory(owner=user, is_reshare=True)
        assert not user.has_perm("activities.change_activity", post)

    def test_non_owner_can_change_activity(self, user):
        post = PostFactory()
        assert not user.has_perm("activities.change_activity", post)

    def test_moderator_can_change_activity(self, moderator):
        post = PostFactory(community=moderator.community)
        assert not moderator.member.has_perm("activities.change_activity", post)


class TestChangeTagsPermissions:
    def test_owner_can_change_activity(self, user):
        post = PostFactory(owner=user)
        assert not user.has_perm("activities.change_activity_tags", post)

    def test_non_owner_can_change_activity(self, user):
        post = PostFactory()
        assert not user.has_perm("activities.change_activity_tags", post)

    def test_moderator_can_change_activity(self, moderator, post):
        assert moderator.member.has_perm("activities.change_activity_tags", post)

    def test_moderator_can_change_own_activity(self, moderator):
        post = PostFactory(owner=moderator.member, community=moderator.community)
        assert not moderator.member.has_perm("activities.change_activity_tags", post)

    def test_moderator_can_change_activity_if_reshare(self, moderator):
        post = PostFactory(community=moderator.community, is_reshare=True)
        assert not moderator.member.has_perm("activities.change_activity_tags", post)

    def test_moderator_can_change_activity_if_deleted(self, moderator):
        post = PostFactory(community=moderator.community, deleted=timezone.now())
        assert not moderator.member.has_perm("activities.change_activity_tags", post)

    def test_moderator_can_change_activity_if_private(self, moderator):
        post = PostFactory(community=moderator.community, published=None)
        assert not moderator.member.has_perm("activities.change_activity_tags", post)


class TestDeletePermissions:
    def test_owner_can_delete_activity(self, user):
        post = PostFactory(owner=user)
        assert user.has_perm("activities.delete_activity", post)

    def test_owner_can_delete_activity_if_deleted(self, user):
        post = PostFactory(owner=user, deleted=timezone.now())
        assert user.has_perm("activities.delete_activity", post)

    def test_owner_can_delete_activity_if_reshare(self, user):
        post = PostFactory(owner=user, is_reshare=True)
        assert user.has_perm("activities.delete_activity", post)

    def test_non_owner_can_delete_activity(self, user):
        post = PostFactory()
        assert not user.has_perm("activities.delete_activity", post)

    def test_moderator_can_delete_activity(self, moderator):
        post = PostFactory(community=moderator.community)
        assert moderator.member.has_perm("activities.delete_activity", post)

    def test_moderator_can_delete_activity_if_deleted(self, moderator):
        post = PostFactory(community=moderator.community, deleted=timezone.now())
        assert not moderator.member.has_perm("activities.delete_activity", post)
