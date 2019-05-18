import pytest

from django.conf import settings
from django.utils.encoding import force_str

from communikit.comments.models import Comment
from communikit.likes.models import Like

pytestmark = pytest.mark.django_db


class TestComments:
    """
    TBD: move these tests under MarkdownField tests
    """
    def test_markdown(self):
        comment = Comment(content="*testing*")
        assert (
            force_str(comment.content.markdown()) == "<p><em>testing</em></p>"
        )

    def test_extract_mentions(self):
        comment = Comment(content="hello @danjac")
        assert comment.content.extract_mentions() == {"danjac"}
