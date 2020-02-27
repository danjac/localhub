# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.encoding import force_str

from ..utils import linkify_hashtags, markdownify


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


class TestLinkifyHashtags:
    def test_linkify(self):
        content = "tags: #coding #opensource #Coding2019 #kesä"
        replaced = linkify_hashtags(content)
        assert (
            replaced == 'tags: <a href="/tags/coding/">#coding</a>'
            ' <a href="/tags/opensource/">#opensource</a>'
            ' <a href="/tags/coding2019/">#Coding2019</a>'
            ' <a href="/tags/kesa/">#kesä</a>'
        )
