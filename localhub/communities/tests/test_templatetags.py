import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Community, Membership
from localhub.communities.templatetags.communities_tags import (
    get_local_communities,
)
from localhub.communities.tests.factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestGetLocalCommunities:
    def test_anonymous_user_if_no_other_community(self, community: Community):
        assert get_local_communities(AnonymousUser(), community).count() == 0

    def test_anonymous_user_if_other_community_public(
        self, community: Community
    ):
        CommunityFactory(public=True)
        assert get_local_communities(AnonymousUser(), community).count() == 1

    def test_anonymous_user_if_other_community_not_public(
        self, community: Community
    ):
        CommunityFactory(public=False)
        assert get_local_communities(AnonymousUser(), community).count() == 0

    def test_user_if_no_other_memberships(
        self, member: settings.AUTH_USER_MODEL
    ):
        assert (
            get_local_communities(member.member, member.community).count() == 0
        )

    def test_user_if_no_other_memberships_if_other_community(
        self, member: settings.AUTH_USER_MODEL
    ):
        community = CommunityFactory(public=True)
        assert get_local_communities(member.member, community).count() == 1

    def test_user_if_other_memberships_if_other_community_not_public(
        self, member: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=member.member, community=CommunityFactory(public=False)
        )
        assert (
            get_local_communities(member.member, member.community).count() == 1
        )
