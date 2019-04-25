import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.communities.models import Community, Membership

pytestmark = pytest.mark.django_db


class TestCommunityModel:
    def test_user_has_role_if_has_role(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert community.user_has_role(user, "member")

    def test_user_has_role_if_has_role_and_inactive(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member", active=False
        )
        assert not community.user_has_role(user, "member")

    def test_user_has_role_if_not_same_role(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert not community.user_has_role(user, "admin")

    def test_user_has_role_if_no_role(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not community.user_has_role(user, "admin")

    def test_user_has_role_if_anonymous(self, community: Community):
        assert not community.user_has_role(AnonymousUser(), "admin")
