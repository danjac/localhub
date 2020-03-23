# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..utils import extract_hashtags, linkify_hashtags


class TestExtractHashtags:
    def test_extract(self):
        content = "tags: #coding #opensource #Coding2019 #kesä"
        assert extract_hashtags(content) == {
            "coding",
            "opensource",
            "coding2019",
            "kesä",
        }


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
