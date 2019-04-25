import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.test.client import RequestFactory

from communikit.communities.models import Community, Membership

from .factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestCommunityManager:
    def test_get_current_if_community_on_site(
        self, req_factory: RequestFactory
    ):

        req = req_factory.get("/", HTTP_HOST="example.com")
        community = CommunityFactory(site=Site.objects.get_current(req))
        assert Community.objects.get_current(req) == community

    def test_get_current_if_inactive_community_on_site(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/", HTTP_HOST="example.com")
        CommunityFactory(site=Site.objects.get_current(req), active=False)
        assert Community.objects.get_current(req) is None

    def test_get_current_if_no_community_available(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/", HTTP_HOST="example.com")
        assert Community.objects.get_current(req) is None

    def test_get_current_if_no_site_available(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/", HTTP_HOST="something-random.example.com")
        assert Community.objects.get_current(req) is None


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
