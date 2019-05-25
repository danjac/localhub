import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership, Community
from communikit.events.tests.factories import EventFactory
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestActivityProfileView:
    def test_get(self, client: Client, member: Membership):
        PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)

        response = client.get(
            reverse("activities:profile", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestActivityStreamView:
    def test_get(self, client: Client, community: Community):
        PostFactory(community=community)
        EventFactory(community=community)

        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestActivitySearchView:
    def test_get(self, client: Client, community: Community):
        post = PostFactory(community=community, title="test")
        event = EventFactory(community=community, title="test")

        for item in (post, event):
            item.make_search_updater()()

        response = client.get(reverse("activities:search"), {"q": "test"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_if_search_string_empty(
        self, client: Client, community: Community
    ):

        response = client.get(reverse("activities:search"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0
