import bleach
import re

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

from bleach.linkifier import LinkifyFilter

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from communikit.communities.models import Community


# TBD : we'll move all this into a separate module we can re-use elsewhere.

ALLOWED_TAGS = bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6"]

cleaner = bleach.Cleaner(ALLOWED_TAGS, filters=[LinkifyFilter])

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)")


def custom_markdownify(content: str) -> str:
    return markdownify(replace_hashtags_in_markdown(content))


def replace_hashtags_in_markdown(s: str) -> str:
    # TBD: we want to have markdownX handle preview without
    # parsing the # tags as h1 etc....
    # therefore need to override basic function
    # break strings into tokens first...
    tokens = s.split(" ")
    rv = []
    # placeholder url
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


class Post(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    title = models.CharField(blank=True, max_length=255)

    url = models.URLField(blank=True)

    description = MarkdownxField(blank=True)

    published = models.DateTimeField(null=True, blank=True)

    objects = InheritanceManager()

    def __str__(self) -> str:
        return self.title or str(f"Post: {self.id}")

    def get_absolute_url(self) -> str:
        return reverse("content:detail", args=[self.id])

    def get_permalink(self) -> str:
        return f"http://{self.community.domain}{self.get_absolute_url()}"

    def markdown(self) -> str:
        return mark_safe(cleaner.clean(custom_markdownify(self.description)))
