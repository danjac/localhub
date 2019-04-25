import pytest

from django.conf import settings

from communikit.communities.models import Community, Membership
from communikit.communities.rules import is_admin, is_moderator, is_member


pytestmark = pytest.mark.django_db


class TestIsAdmin:
    def test_is_admin_if_user_not_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin(user, community)
        assert not is_moderator(user, community)
        assert not is_member(user, community)

    def test_is_admin_if_user_is_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert is_admin(user, community)
        assert is_moderator(user, community)
        assert is_member(user, community)


class TestIsModerator:
    def test_is_moderator_if_user_not_moderator(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin(user, community)
        assert not is_moderator(user, community)
        assert not is_member(user, community)

    def test_is_moderator_if_user_is_moderator(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="moderator"
        )
        assert not is_admin(user, community)
        assert is_moderator(user, community)
        assert is_member(user, community)


class TestIsMember:
    def test_is_member_if_user_not_member(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin(user, community)
        assert not is_moderator(user, community)
        assert not is_member(user, community)

    def test_is_member_if_user_is_member(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert not is_admin(user, community)
        assert not is_moderator(user, community)
        assert is_member(user, community)
