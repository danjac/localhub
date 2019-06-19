# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from celery import shared_task
from celery.utils.log import get_task_logger

from communikit.posts.models import Post

logger = get_task_logger(__name__)


@shared_task(name="posts.fetch_title_from_url")
def fetch_title_from_url(post_id: int):
    try:
        post = Post.objects.get(pk=post_id)
        if post.url and not post.title:
            response = requests.get(post.url)
            if response.ok:
                soup = BeautifulSoup(response.content, "html.parser")
                post.title = (soup.title.string or urlparse(post.url).netloc)[
                    :300
                ]
                post.save()
    except Post.DoesNotExist:
        logger.info("post not found:%s", post_id)
