# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from celery import shared_task
from celery.utils.log import get_task_logger

from localhub.posts.models import Post
from localhub.posts.utils import fetch_title_from_url

logger = get_task_logger(__name__)


@shared_task(name="posts.fetch_post_title_from_url")
def fetch_post_title_from_url(post_id):
    try:
        post = Post.objects.get(pk=post_id)
        if post.url and not post.title:
            post.title = (fetch_title_from_url(post.url) or post.get_domain())[
                :300
            ]
            post.save(update_fields=["title"])
    except Post.DoesNotExist:
        logger.info("post not found:%s", post_id)
