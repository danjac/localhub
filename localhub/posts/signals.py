# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from celery.utils.log import get_logger

from localhub.posts import tasks
from localhub.posts.models import Post

celery_logger = get_logger(__name__)


@receiver(post_save, sender=Post, dispatch_uid="posts.fetch_title_from_url")
def fetch_title_from_url(instance, **kwargs):
    if not instance.url or instance.title:
        return

    def run_task():
        try:
            tasks.fetch_post_title_from_url.delay(instance.id)
        except tasks.fetch_post_title_from_url.OperationalError as e:
            celery_logger.exception(e)

    transaction.on_commit(run_task)
