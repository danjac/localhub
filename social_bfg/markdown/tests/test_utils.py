# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.encoding import force_str

# Local
from ..utils import markdownify


class TestMarkdownifySafe:
    def test_markdownify_with_safe_tags(self):
        content = "*testing*"
        assert force_str(markdownify(content)) == "<p><em>testing</em></p>"

    def test_markdownify_with_dangerous_tags(self):
        content = "<script>alert('howdy');</script>"
        assert (
            force_str(markdownify(content))
            == "&lt;script&gt;alert('howdy');&lt;/script&gt;"
        )

    def test_markdownify_with_mention(self):
        content = "hello @danjac"
        md = force_str(markdownify(content))
        assert 'data-controller="hovercard"' in md

    def test_markdownify_with_links(self):
        content = "Reddit: http://reddit.com"
        md = force_str(markdownify(content))
        assert "nofollow" in md
        assert 'target="_blank"' in md
