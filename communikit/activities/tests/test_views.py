import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Community
from communikit.events.tests.factories import EventFactory
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestActivityStreamView:
    def test_get(self, client: Client, community: Community):
        PostFactory(community=community)
        EventFactory(community=community)

        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
