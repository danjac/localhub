from django.utils.encoding import force_str

from localite.core.markdown.utils import (
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
        content = "hello @danjac and @weegill and @someone-else!"
        assert extract_mentions(content) == {
            "danjac",
            "weegill",
            "someone-else",
        }


class TestLinkifyMentions:
    def test_linkify(self):
        content = "hello @danjac"
        replaced = linkify_mentions(content)
        assert replaced == 'hello <a href="/people/danjac/">@danjac</a>'


class TestLinkifyHashtags:
    def test_linkify(self):
        content = "tags: #coding #opensource #coding2019"
        replaced = linkify_hashtags(content)
        assert (
            replaced == 'tags: <a href="/tag/coding/">#coding</a>'
            ' <a href="/tag/opensource/">#opensource</a>'
            ' <a href="/tag/coding2019/">#coding2019</a>'
        )
