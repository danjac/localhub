# Third Party Libraries
import pytest

# Local
from ..context_processors import community
from ..factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestCommunityContextProcessor:
    def test_community(self, rf):
        req = rf.get("/")
        req.community = CommunityFactory()
        context = community(req)
        assert context["community"] == req.community
