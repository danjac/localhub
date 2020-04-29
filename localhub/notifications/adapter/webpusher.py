# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.templatetags.static import static
from django.utils.encoding import force_text

from celery.utils.log import get_logger

celery_logger = get_logger(__name__)


class Webpusher:
    def __init__(self, adapter):
        self.adapter = adapter

    def send(self):
        """
        Sends a webpush notification to registered browsers through celery.
        """
        from .. import tasks

        try:
            return tasks.send_webpush.delay(
                self.adapter.recipient.id, self.adapter.community.id, self.get_payload()
            )
        except tasks.send_webpush.OperationalError as e:
            celery_logger.exception(e)

    def get_header(self):
        return str(self.adapter.object)

    def get_body(self):
        return None

    def get_url(self):
        return self.adapter.get_absolute_url()

    def get_payload(self):

        payload = {
            "head": self.get_header(),
            "url": self.get_url(),
        }

        if body := self.get_body():
            payload["body"] = force_text(body)

        if self.adapter.community.logo:
            payload["icon"] = self.adapter.community.logo.url
        else:
            payload["icon"] = static("favicon.png")

        return payload
