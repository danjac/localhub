# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from localhub.posts import tasks
from localhub.posts.models import Post


@receiver(post_save, sender=Post, dispatch_uid="posts.fetch_title_from_url")
def fetch_title_from_url(instance: Post, **kwargs):
    transaction.on_commit(
        lambda: tasks.fetch_post_title_from_url.delay(instance.id)
    )


@receiver(post_save, sender=Post, dispatch_uid="posts.update_search_document")
def update_search_document(instance: Post, **kwargs):
    transaction.on_commit(lambda: instance.search_indexer.update())


@receiver(post_save, sender=Post, dispatch_uid="posts.taggit")
def taggit(instance: Post, created: bool, **kwargs):
    transaction.on_commit(lambda: instance.taggit(created))
