import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from communikit.communities.models import Membership

from .factories import CommunityFactory

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestCommunityModel:
    def test_user_has_role_if_has_role(self, user: settings.AUTH_USER_MODEL):
        community = CommunityFactory()
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert community.user_has_role(user, "member")

    def test_user_has_role_if_not_same_role(
        self, user: settings.AUTH_USER_MODEL
    ):
        community = CommunityFactory()
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert not community.user_has_role(user, "admin")

    def test_user_has_role_if_no_role(self, user: settings.AUTH_USER_MODEL):
        community = CommunityFactory()
        assert not community.user_has_role(user, "admin")

    def test_user_has_role_if_anonymous(self):
        community = CommunityFactory()
        assert not community.user_has_role(AnonymousUser(), "admin")
