import pytest

from communikit.activities.templatetags.activities_tags import model_name
from communikit.posts.tests.factories import PostFactory
from communikit.events.tests.factories import EventFactory

pytestmark = pytest.mark.django_db


class TestModelName:
    def test_if_post(self):
        post = PostFactory()
        assert model_name(post) == "post"

    def test_if_event(self):
        event = EventFactory()
        assert model_name(event) == "event"
