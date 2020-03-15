# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery.utils.log import get_logger
from django.core.mail import send_mail
from django.template import loader, Context
from django.utils.encoding import force_text
from django.utils.translation import override


from . import tasks


celery_logger = get_logger(__name__)


class BaseNotificationAdapter:
    def __init__(self, notification):
        self.notification = notification
        self.verb = self.verb
        self.object = self.notification.content_object
        self.recipient = self.notification.recipient
        self.actor = self.notification.actor
        self.community = self.notification.community

    def send_notification(self):
        with override(self.recipient.language):
            self.send_webpush()
            self.send_email()

    def send_webpush(self):
        try:
            return tasks.webpush.delay(
                self.recipient.id, self.community.id, self.get_webpush_payload()
            )
        except tasks.send_webpush.OperationalError as e:
            celery_logger.exception(e)

    def send_email(self, **kwargs):
        if self.recipient.send_email_notifications:
            subject = self.get_email_subject()
            context = self.get_email_context()

            plain_content = loader.render_to_string(
                self.get_plain_email_template_names(), context
            )
            html_content = loader.render_to_string(
                self.get_html_email_template_names(), context
            )

            return send_mail(
                f"{self.community.name} | {subject}",
                plain_content,
                self.get_email_sender(),
                [self.recipient.email],
                html_content,
                **kwargs,
            )

    def render_to_template(self, template_engine, extra_context=None):
        return template_engine.select_template(self.get_template_names).render(
            Context(self.get_template_context(extra_context or {}))
        )

    def get_object_url(self):
        return self.object.get_absolute_url()

    def get_absolute_url(self):
        return self.community.resolve_url(self.get_object_url())

    def resolve_template_path(self, suffix):
        """
        Example:
        posts/emails/notification.html
        posts/includes/notification.html
        """
        return [
            "%s/%s%s"
            % (
                self.object._meta.app_label,
                self.object._meta.object_name.lower(),
                suffix,
            )
        ]

    def get_template_names(self):
        return [
            self.resolve_template_path(f"notifications/includes/{self.verb}.html"),
            self.resolve_template_path("notifications/includes/notification.html"),
        ]

    def get_plain_email_template_names(self):
        return [
            self.resolve_template_path(f"emails/notifications/{self.verb}.txt"),
            self.resolve_template_path("emails/notifications/notification.txt"),
        ]

    def get_html_email_template_names(self):
        return [
            self.resolve_template_path(f"emails/notifications/{self.verb}.html"),
            self.resolve_template_path(f"emails/notifications/notification.html"),
        ]

    def get_content_object_name(self):
        return self.object._meta.model_name

    def get_template_context(self, extra_context):
        context = {
            "notification": self.notification,
            "object": self.object,
            "object_url": self.get_object_url(),
            "recipient": self.recipient,
            "actor": self.actor,
            "verb": self.verb,
            "absolute_url": self.get_absolute_url(),
            self.get_content_object_name(): self.object,
        }
        context.update(extra_context)
        return context

    def get_email_subject(self):
        return str(self.object)

    def get_email_sender(self):
        return self.community.resolve_email("no-reply")

    def get_email_context(self):
        return self.get_context()

    def get_webpush_header(self):
        return str(self.object)

    def get_webpush_body(self):
        return str(self.object)

    def get_webpush_url(self):
        return self.get_absolute_url()

    def get_webpush_payload(self):
        return {
            "head": self.get_webpush_header(),
            "body": force_text(self.get_webpush_body()),
            "url": self.get_webpush_url(),
        }
