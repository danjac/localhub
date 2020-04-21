# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod

from django.template import loader
from django.utils.translation import override

from .mailer import Mailer
from .template import TemplateContext, TemplateRenderer, TemplateResolver
from .webpusher import Webpusher

__all__ = [
    "Adapter",
    "DefaultAdapter",
    "Mailer",
    "TemplateContext",
    "TemplateRenderer",
    "TemplateResolver",
    "Webpusher",
]


class Adapter(ABC):
    @abstractmethod
    def send_notification(self):
        ...

    @abstractmethod
    def render_to_tag(self, template_engine=loader, extra_context=None):
        ...


class DefaultAdapter(Adapter):
    """
    Base class for handling notifications. All adapters should subclass
    this class.

    Supports:
    1. Rendering notification to html template
    2. Sending plain/HTML emails
    3. Webpush support

    Subclasses must define ALLOWED_VERBS for all notifications they support.

    If a notification verb is not in the list of ALLOWED_VERBS the notification
    will not be sent or rendered.
    """

    webpusher_class = Webpusher
    mailer_class = Mailer

    context_class = TemplateContext
    renderer_class = TemplateRenderer
    resolver_class = TemplateResolver

    # provide list of verbs accepted by this adapter.

    ALLOWED_VERBS = []

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

    def is_allowed(self):
        """
        Check if notification verb is in list of ALLOWED_VERBS
        for this adapter.

        Returns:
            bool
        """
        return self.verb in self.ALLOWED_VERBS

    def send_notification(self):
        """
        Sends email and webpush notifications localized to
        recipient language.
        """
        with override(self.recipient.language):
            self.mailer.send()
            self.webpusher.send()

    def get_template_names(self):
        """Returns path of template names using TemplateResolver

        Returns:
            list: list of template paths
        """
        return self.resolver.resolve(f"{self.app_label}/includes")

    def get_object_url(self):
        """Calls content_object.get_absolute_url()

        Returns:
            str: object URL
        """
        return self.object.get_absolute_url()

    def get_absolute_url(self):
        """Prepends the complete community URL to get_object_url(), for
        example https://demo.localhub.social/posts/path-to-single-post/

        Returns:
            str: absolute URL
        """
        return self.community.resolve_url(self.get_object_url())

    def render_to_tag(self, template_engine=loader, extra_context=None):
        """Used with the {% notification %} template tag under notification_tags.

        It should render an HTML snippet of the notification
        in the notifications page and other parts of the site.

        Args:
           template_engine (optional): Django template engine (default: loader)
           extra_context (dict, optional): additional context (default: None)

        Returns:
           str: rendered template str
        """
        return self.renderer.render(
            self.get_template_names(),
            self.context.get_context(extra_context),
            template_engine=template_engine,
        )
