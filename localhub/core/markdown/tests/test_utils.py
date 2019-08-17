from django.utils.encoding import force_str

from localhub.core.markdown.utils import (
    extract_mentions,
    linkify_hashtags,
    linkify_mentions,
    markdownify,
)


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


class TestExtractMentions:
    def test_extract(self):
        content = "hello @danjac and @weegill and @kesämies and @someone-else!"
        assert extract_mentions(content) == {
            "danjac",
            "weegill",
            "kesämies",
            "someone-else",
        }


class TestLinkifyMentions:
    def test_linkify(self):
        content = "hello @danjac"
        replaced = linkify_mentions(content)
        assert replaced == 'hello <a href="/people/danjac/">@danjac</a>'

    def test_linkify_unicode(self):
        content = "hello @kesämies"
        replaced = linkify_mentions(content)
        assert replaced == 'hello <a href="/people/kesamies/">@kesämies</a>'


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
