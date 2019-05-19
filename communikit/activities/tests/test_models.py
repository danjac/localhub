import pytest

from communikit.activities.models import Activity
from communikit.comments.models import Comment

pytestmark = pytest.mark.django_db


class TestActivityQuerySet:
    def test_with_num_comments(self, comment: Comment):
        activity = Activity.objects.with_num_comments().get()
        assert activity.num_comments == 1
