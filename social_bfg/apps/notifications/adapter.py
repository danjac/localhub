# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.templatetags.static import static
from django.utils.encoding import force_text
from django.utils.translation import override

# Third Party Libraries
from celery.utils.log import get_logger

celery_logger = get_logger(__name__)


class TemplateRenderer:
    """Renders notification to template.
    """

    def __init__(self, adapter, prefixes):
        """
        Args:
            adapter (Adapter)
            prefixes (List[str]): list of template prefixes to prepend to template names
        """

        self.adapter = adapter
        self.prefixes = prefixes

    def get_template_names(self, suffix=".html"):
        """Generates list of standard Django template paths. Can
        be passed to loader.select_template() or similar.

        Pattern:
        {prefix}/{verb}_{object_name}{suffix}
        {prefix}/{verb}{suffix}
        {prefix}/{object_name}_notification{suffix}
        {prefix}/notification{suffix}

        Args:
            suffix (str): suffix appended to all paths e.g. ".txt"

        Returns:
            list: list of path strs
        """
        return [
            path
            for prefix in self.prefixes
            for path in [
                f"{prefix}/notifications/{self.adapter.verb}_{self.adapter.object_name}{suffix}",
                f"{prefix}/notifications/{self.adapter.verb}{suffix}",
                f"{prefix}/{self.adapter.object_name}_notification{suffix}",
                f"{prefix}/notification{suffix}",
            ]
        ]

    def get_context(self, extra_context=None):
        """Returns context containing useful notification info:

        - notification: the Notification instance
        - object: content object attached to Notification
        - object_url: result of content_object.get_absolute_url()
        - absolute_url: object_url prefixed by complete URL of community
        - object_name: object verbose name e.g. "post"
        - actor: actor User instance
        - actor_display: full name of actor
        - recipient: recipient User instance
        - recipient_display: full name of recipient
        - verb: e.g. "mention"

        Args:
            extra_context (dict): additional context (default: None)

        Returns:
            dict: template context
        """
        context = self.adapter.as_dict()
        context.update(extra_context or {})
        return context

    def render(self, extra_context=None, template_engine=loader, suffix=".html"):
        """Renders a list of templates to a str. Use with TemplateResolver
        and TemplateContext.

        Args:
            extra_context (dict): template context
            template_engine (object, optional): Django template engine (default: loader)

        Returns:
            str: rendered template
        """
        return template_engine.render_to_string(
            self.get_template_names(suffix), context=self.get_context(extra_context),
        )


class Mailer:
    """
    Manages Notification plain and HTML emails.
    """

    renderer_class = TemplateRenderer
    sender_address = "no-reply"

    def __init__(self, adapter):
        self.adapter = adapter
        self.renderer = self.renderer_class(self.adapter, self.get_template_prefixes())

    def send(self, **kwargs):
        recipient = self.get_recipient()

        if recipient.send_email_notifications:
            subject = self.get_subject()
            context = {"subject": subject}

            return send_mail(
                f"{self.adapter.community.name} | {subject}",
                self.renderer.render(suffix=(".txt"), extra_context=context),
                self.get_sender(),
                [recipient.email],
                html_message=self.renderer.render(
                    suffix=".html", extra_context=context
                ),
                **kwargs,
            )

    def get_subject(self):
        return str(self.adapter.object)

    def get_sender(self):
        return self.adapter.community.resolve_email(self.sender_address)

    def get_recipient(self):
        return self.adapter.recipient

    def get_template_prefixes(self):
        return [f"{self.adapter.app_label}/emails"]


class Webpusher:
    def __init__(self, adapter):
        self.adapter = adapter

    def send(self):
        """
        Sends a webpush notification to registered browsers through celery.
        """
        if settings.SOCIAL_BFG_WEBPUSH_ENABLED:
            from . import tasks

            try:
                return tasks.send_webpush.delay(
                    self.adapter.recipient.id,
                    self.adapter.community.id,
                    self.get_payload(),
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

        payload["icon"] = static("favicon.png")

        return payload


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
        example https://demo.social_bfg.social/posts/path-to-single-post/

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
