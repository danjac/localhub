# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod

from celery.utils.log import get_logger
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_text
from django.utils.translation import override

from localhub.users.utils import user_display

celery_logger = get_logger(__name__)


class NotificationAdapter(ABC):
    @abstractmethod
    def send_notification(self):
        ...

    @abstractmethod
    def render_to_template(self, template_engine=loader, extra_context=None):
        ...


class TemplateContext:
    def __init__(self, adapter):
        self.adapter = adapter

    def get_context(self, extra_context=None):
        context = {
            "notification": self.adapter.notification,
            "object": self.adapter.object,
            "object_url": self.adapter.get_object_url(),
            "absolute_url": self.adapter.get_absolute_url(),
            "object_name": self.adapter.object_name,
            "actor": self.adapter.actor,
            "actor_display": user_display(self.adapter.actor),
            "recipient": self.adapter.recipient,
            "recipient_display": user_display(self.adapter.recipient),
            "verb": self.adapter.verb,
            self.adapter.object_name: self.adapter.object,
        }
        context.update(extra_context or {})
        return context


class TemplateResolver:
    def __init__(self, adapter):
        self.adapter = adapter
        self.verb = self.adapter.verb
        self.object_name = self.adapter.object_name

    def resolve(self, prefix, suffix=".html"):
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


class TemplateRenderer:
    def render(
        self, template_names, context, template_engine=loader,
    ):
        return template_engine.render_to_string(template_names, context=context,)


class Webpusher:
    def __init__(self, adapter):
        self.adapter = adapter
        self.object = self.adapter.object
        self.recipient = self.adapter.recipient
        self.community = self.adapter.community

    def send(self):
        """
        Sends a webpush notification to registered browsers through celery.
        """
        from . import tasks

        try:
            return tasks.send_webpush.delay(
                self.recipient.id, self.community.id, self.get_payload()
            )
        except tasks.send_webpush.OperationalError as e:
            celery_logger.exception(e)

    def get_header(self):
        return str(self.object)

    def get_body(self):
        return str(self.object)

    def get_url(self):
        return self.adapter.get_absolute_url()

    def get_payload(self):
        return {
            "head": self.get_header(),
            "body": force_text(self.get_body()),
            "url": self.get_url(),
        }


class Mailer:

    resolver_class = TemplateResolver
    renderer_class = TemplateRenderer
    context_class = TemplateContext

    def __init__(self, adapter):
        self.adapter = adapter

        self.community = self.adapter.community
        self.recipient = self.adapter.recipient
        self.app_label = self.adapter.app_label

        self.renderer = self.renderer_class()
        self.resolver = self.resolver_class(self.adapter)
        self.context = self.context_class(self.adapter)

    def get_template_names(self, suffix):
        return self.resolver.resolve(f"{self.app_label}/emails", suffix)

    def send(self, **kwargs):
        if self.recipient.send_email_notifications:
            subject = self.get_subject()
            context = self.context.get_context({"subject": subject})

            return send_mail(
                f"{self.community.name} | {subject}",
                self.renderer.render(self.get_template_names(".txt"), context),
                self.get_sender(),
                [self.recipient.email],
                self.renderer.render(self.get_template_names(".html"), context),
                **kwargs,
            )

    def get_subject(self):
        return str(self.object)

    def get_sender(self):
        return self.community.resolve_email("no-reply")


class BaseNotificationAdapter(NotificationAdapter):
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

    webpusher_class = Webpusher
    mailer_class = Mailer

    context_class = TemplateContext
    renderer_class = TemplateRenderer
    resolver_class = TemplateResolver

    def __init__(self, notification):

        self.notification = notification
        self.verb = self.notification.verb
        self.recipient = self.notification.recipient
        self.actor = self.notification.actor
        self.community = self.notification.community

        self.object = self.notification.content_object
        self.object_name = self.object._meta.object_name.lower()
        self.app_label = self.object._meta.app_label

        self.renderer = self.renderer_class()
        self.resolver = self.resolver_class(self)
        self.context = self.context_class(self)

        self.mailer = self.mailer_class(self)
        self.webpusher = self.webpusher_class(self)

    def send_notification(self):
        """
        Sends email and webpush notifications localized to
        recipient language.
        """
        with override(self.recipient.language):
            self.mailer.send()
            self.webpusher.send()

    def get_template_names(self):
        return self.resolver.resolve(f"{self.app_label}/includes")

    def get_object_url(self):
        return self.object.get_absolute_url()

    def get_absolute_url(self):
        return self.community.resolve_url(self.get_object_url())

    def render_to_template(self, template_engine=loader, extra_context=None):
        """
        This is used with the {% render_notification %} template tag in
        notification_tags. It should render an HTML snippet of the notification
        in the notifications page and other parts of the site.
        """
        return self.renderer.render(
            self.get_template_names(),
            self.context.get_context(extra_context),
            template_engine=template_engine,
        )
