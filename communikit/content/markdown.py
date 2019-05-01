import re
import bleach

from bleach.linkifier import LinkifyFilter

from django.urls import reverse

from markdownx.utils import markdownify as default_markdownify

ALLOWED_TAGS = bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6"]

cleaner = bleach.Cleaner(ALLOWED_TAGS, filters=[LinkifyFilter])

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)")


def markdownify(content: str) -> str:
    """
    Drop-in replacement to default MarkdownX markdownify function.

    - Linkifies URLs, @mentions and #hashtags
    - Restricts permitted HTML tags to safer subset

    """
    return cleaner.clean(
        default_markdownify(linkify_hashtags(linkify_mentions(content)))
    )


def linkify_mentions(content: str) -> str:
    """
    Replace all @mentions in the text with links to profile page.
    """

    tokens = content.split(" ")
    rv = []
    # placeholder url until we have some suitable views
    search_url = reverse("content:list")
    for token in tokens:

        for mention in MENTIONS_RE.findall(token):
            url = search_url + f"?profile={mention}"
            token = token.replace(
                "@" + mention, f'<a href="{url}">@{mention}</a>'
            )

        rv.append(token)

    return " ".join(rv)


def linkify_hashtags(content: str) -> str:
    """
    Replace all #hashtags in text with links to some tag search page.
    """
    tokens = content.split(" ")
    rv = []
    # placeholder url until we have some suitable views
    search_url = reverse("content:list")
    for token in tokens:

        for tag in HASHTAGS_RE.findall(token):
            url = search_url + f"?hashtag={tag}"
            token = token.replace("#" + tag, f'<a href="{url}">#{tag}</a>')

        rv.append(token)

    return " ".join(rv)
