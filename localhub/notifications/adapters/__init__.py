# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import override

from .mailer import Mailer
from .template import TemplateRenderer
from .webpusher import Webpusher

__all__ = [
    "Adapter",
    "Mailer",
    "TemplateRenderer",
    "Webpusher",
]


class Adapter:
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
    renderer_class = TemplateRenderer

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

        self.mailer = self.mailer_class(self)
        self.webpusher = self.webpusher_class(self)

        self.renderer = self.renderer_class(self, self.get_template_prefixes())

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

    def get_template_prefixes(self):
        """Returns list of default template name prefixes
        used to render the notification template tag.

        Returns:
            List[str]
        """
        return [f"{self.app_label}/includes"]

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

    def render_to_tag(self, **template_kwargs):
        """Used with the {% notification %} template tag under notification_tags.

        It should render an HTML snippet of the notification
        in the notifications page and other parts of the site.

        Args:
           template_engine (optional): Django template engine (default: loader)
           extra_context (dict, optional): additional context (default: None)

        Returns:
           str: rendered template str
        """
        return self.renderer.render(**template_kwargs)

    def as_dict(self):
        """Serialize this object as a dict with all
        required notification and object references.

        Returns:
            dict
        """
        actor_url = self.actor.get_absolute_url()
        recipient_url = self.recipient.get_absolute_url()

        return {
            "actor_url": actor_url,
            "recipient_url": recipient_url,
            "notification": self.notification,
            "object": self.object,
            "object_url": self.get_object_url(),
            "absolute_url": self.get_absolute_url(),
            "object_name": self.object_name,
            "actor": self.actor,
            "actor_display": self.actor.get_display_name(),
            "actor_absolute_url": self.community.resolve_url(actor_url),
            "recipient": self.recipient,
            "recipient_display": self.recipient.get_display_name(),
            "recipient_absolute_url": self.community.resolve_url(recipient_url),
            "verb": self.verb,
            self.object_name: self.object,
        }
