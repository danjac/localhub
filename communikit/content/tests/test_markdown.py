from django.utils.encoding import force_str

from communikit.content.markdown import (
    replace_hashtags_in_markdown,
    markdownify,
)


class TestMarkdownifySafe:
    def test_markdownify_with_safe_tags(self):
        content = "*testing*"
        assert (
            force_str(markdownify(content)) == "<p><em>testing</em></p>"
        )

    def test_markdownify_with_dangerous_tags(self):
        content = "<script>alert('howdy');</script>"
        assert (
            force_str(markdownify(content))
            == "&lt;script&gt;alert('howdy');&lt;/script&gt;"
        )


class TestReplaceHashtagsInMarkdown:
    def test_replace_mentions(self):
        content = "hello @danjac"
        replaced = replace_hashtags_in_markdown(content)
        assert replaced == "hello [@danjac](/?profile=danjac)"

    def test_replace_hashtags(self):
        content = "tags: #coding #opensource #coding2019"
        replaced = replace_hashtags_in_markdown(content)
        assert (
            replaced == "tags: [\\#coding](/?hashtag=coding) "
            "[\\#opensource](/?hashtag=opensource) "
            "[\\#coding2019](/?hashtag=coding2019)"
        )
