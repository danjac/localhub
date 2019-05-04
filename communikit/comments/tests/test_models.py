import pytest

from django.utils.encoding import force_str

from communikit.comments.models import Comment

pytestmark = pytest.mark.django_db


class TestComments:
    def test_markdown(self):
        comment = Comment(content="*testing*")
        assert force_str(comment.markdown()) == "<p><em>testing</em></p>"
