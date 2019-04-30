from django.utils.encoding import force_str

from communikit.content.markdown import (
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


class TestLinkifyMentions:
    def test_linkify(self):
        content = "hello @danjac"
        replaced = linkify_hashtags(content)
        assert replaced == 'hello <a href="/?profile=danjac">@danjac</a>'


class TestLinkifyHashtags:
    def test_linkify(self):
        content = "tags: #coding #opensource #coding2019"
        replaced = linkify_mentions(content)
        assert (
            replaced == 'tags: <a href="/?hashtag=coding">coding</a>'
            '<a href="/?hashtag=opensource">opensource</a>'
            '<a href="/?hashtag=coding2019">coding2019</a>'
        )
