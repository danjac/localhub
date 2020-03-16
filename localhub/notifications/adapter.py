# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery.utils.log import get_logger
from django.core.mail import send_mail
from django.template import Context, loader
from django.utils.encoding import force_text
from django.utils.translation import override

from localhub.users.utils import user_display

from . import tasks

celery_logger = get_logger(__name__)


class BaseNotificationAdapter:
    """
    Base class for handling notifications. All adapters should subclass
    this class.

    Supports:
    1. Rendering notification to html template
    2. Sending plain/HTML emails
    3. Webpush support

    All Notification content objects should include either the
    notification_adapter_class attribute or implement a
    get_notification_adapter() method.
    """

    def __init__(self, notification):
        self.notification = notification
        self.verb = self.notification.verb
        self.recipient = self.notification.recipient
        self.actor = self.notification.actor
        self.community = self.notification.community

        self.object = self.notification.content_object
        self.object_name = self.object._meta.object_name.lower()
        self.app_label = self.object._meta.app_label

    def send_notification(self):
        """
        Sends email and webpush notifications localized to
        recipient language.
        """
        with override(self.recipient.language):
            self.send_webpush()
            self.send_email()

    def send_webpush(self):
        """
        Sends a webpush notification to registered browsers through celery.
        """
        try:
            return tasks.send_webpush.delay(
                self.recipient.id, self.community.id, self.get_webpush_payload()
            )
        except tasks.send_webpush.OperationalError as e:
            celery_logger.exception(e)

    def send_email(self, **kwargs):
        """
        Send an HTML and plain text email.
        """
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

    def render_to_template(self, template_engine=loader, extra_context=None):
        """
        This is used with the {% render_notification %} template tag in
        notification_tags. It should render an HTML snippet of the notification
        in the notifications page and other parts of the site.
        """
        return template_engine.select_template(self.get_template_names()).render(
            Context(self.get_template_context(extra_context or {}))
        )

    def get_object_url(self):
        return self.object.get_absolute_url()

    def get_absolute_url(self):
        return self.community.resolve_url(self.get_object_url())

    def resolve_template_names(self, prefix, suffix=".html"):
        """
        Pattern:
        {prefix}/{verb}_{object_name}{suffix}
        {prefix}/{verb}{suffix}
        {prefix}/{object_name}_notification{suffix}
        {prefix}/notification{suffix}
         """
        return [
            f"{prefix}/notifications/{self.verb}_{self.object_name}{suffix}",
            f"{prefix}/notifications/{self.verb}{suffix}",
            f"{prefix}/{self.object_name}_notification{suffix}",
            f"{prefix}/notification{suffix}",
        ]

    def get_template_names(self):
        return self.resolve_template_names(f"{self.app_label}/includes")

    def get_plain_email_template_names(self):
        return self.resolve_template_names(f"{self.app_label}/emails", ".txt")

    def get_html_email_template_names(self):
        return self.resolve_template_names(f"{self.app_label}/emails", ".html")

    def get_template_context(self, extra_context=None):
        context = {
            "notification": self.notification,
            "object": self.object,
            "object_url": self.get_object_url(),
            "object_name": self.object_name,
            "actor": self.actor,
            "actor_display": user_display(self.actor),
            "recipient": self.recipient,
            "recipient_display": user_display(self.recipient),
            "verb": self.verb,
            "absolute_url": self.get_absolute_url(),
            self.object_name: self.object,
        }
        context.update(extra_context or {})
        return context

    def get_email_subject(self):
        return str(self.object)

    def get_email_sender(self):
        return self.community.resolve_email("no-reply")

    def get_email_context(self, extra_context=None):
        return self.get_template_context(extra_context)

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
