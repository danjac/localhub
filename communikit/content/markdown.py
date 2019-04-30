import re
import bleach

from django.urls import reverse
from django.utils.safestring import mark_safe

from bleach.linkifier import LinkifyFilter
from markdownx.utils import markdownify as default_markdownify

ALLOWED_TAGS = bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6"]

cleaner = bleach.Cleaner(ALLOWED_TAGS, filters=[LinkifyFilter])

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)")


def markdownify(content: str) -> str:
    return default_markdownify(replace_hashtags_in_markdown(content))


def markdownify_safe(content: str) -> str:
    return mark_safe(cleaner.clean(markdownify(content)))


def replace_hashtags_in_markdown(s: str) -> str:
    tokens = s.split(" ")
    rv = []
    # placeholder url until we have some suitable views
    search_url = reverse("content:list")
    for token in tokens:
        for mention in MENTIONS_RE.findall(token):
            url = search_url + f"?profile={mention}"
            markdown = f"[@{mention}]({url})"
            token = token.replace("@" + mention, markdown)

        for hashtag in HASHTAGS_RE.findall(token):
            url = search_url + f"?hashtag={hashtag}"
            markdown = f"[\\#{hashtag}]({url})"
            token = token.replace("#" + hashtag, markdown)

        rv.append(token)

    return " ".join(rv)
