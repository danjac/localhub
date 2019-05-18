from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from communikit.posts.models import Post


@receiver(post_save, sender=Post, dispatch_uid="posts.update_search_document")
def update_search_document(instance: Post, **kwargs):
    transaction.on_commit(instance.make_search_updater())
