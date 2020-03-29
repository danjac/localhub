# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod

from celery.utils.log import get_logger
from django.core.mail import send_mail
from django.template import loader
from django.templatetags.static import static
from django.utils.encoding import force_text
from django.utils.translation import override

from localhub.users.utils import user_display

celery_logger = get_logger(__name__)


class Adapter(ABC):
    @abstractmethod
    def send_notification(self):
        ...

    @abstractmethod
    def render_to_tag(self, template_engine=loader, extra_context=None):
        ...


class TemplateContext:
    """
    Default template context for emails and HTML notifications.
    """

    def __init__(self, adapter):
        self.adapter = adapter

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
    """
    Resolves selection of template paths for a notification.
    """

    def __init__(self, adapter):
        self.adapter = adapter
        self.verb = self.adapter.verb
        self.object_name = self.adapter.object_name

    def resolve(self, prefix, suffix=".html"):
        """Generates list of standard Django template paths. Can
        be passed to loader.select_template() or similar.

        Pattern:
        {prefix}/{verb}_{object_name}{suffix}
        {prefix}/{verb}{suffix}
        {prefix}/{object_name}_notification{suffix}
        {prefix}/notification{suffix}

        Arguments:
            prefix (str): prefix prepended to all the paths e.g. "post"
            suffix (str): suffix appended to all paths e.g. ".txt"

        Returns:
            list: list of path strs
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
        """Renders a list of templates to a str. Use with TemplateResolver
        and TemplateContext.

        Args:
            template_names (list): list of standard Django template paths
            context (dict): template context
            template_engine (object, optional): Django template engine (default: loader)

        Returns:
            str: rendered template
        """
        return template_engine.render_to_str(template_names, context=context)


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
        return None

    def get_url(self):
        return self.adapter.get_absolute_url()

    def get_payload(self):

        payload = {
            "head": self.get_header(),
            "url": self.get_url(),
        }

        body = self.get_body()
        if body:
            payload["body"] = force_text(body)

        if self.community.logo:
            payload["icon"] = self.community.logo.url
        else:
            payload["icon"] = static("favicon.png")

        return payload


class Mailer:
    """
    Manages Notification plain and HTML emails.
    """

    resolver_class = TemplateResolver
    renderer_class = TemplateRenderer
    context_class = TemplateContext

    def __init__(self, adapter):
        self.adapter = adapter

        self.object = self.adapter.object
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
                html_message=self.renderer.render(
                    self.get_template_names(".html"), context
                ),
                **kwargs,
            )

    def get_subject(self):
        return str(self.object)

    def get_sender(self):
        return self.community.resolve_email("no-reply")


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
