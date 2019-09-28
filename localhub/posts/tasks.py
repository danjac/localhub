# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from celery import shared_task
from celery.utils.log import get_task_logger

from localhub.posts.models import Post

logger = get_task_logger(__name__)


@shared_task(name="posts.fetch_post_metadata_from_url")
def fetch_post_metadata_from_url(post_id):
    try:
        Post.objects.get(pk=post_id).fetch_metadata_from_url()
    except Post.DoesNotExist:
        logger.info("Post not found:%s", post_id)
