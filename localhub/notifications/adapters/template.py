# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Template helper classes for default Adapter base class.
"""

import itertools

from django.template import loader


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
        actor_url = self.adapter.actor.get_absolute_url()
        recipient_url = self.adapter.recipient.get_absolute_url()

        context = {
            "notification": self.adapter.notification,
            "object": self.adapter.object,
            "object_url": self.adapter.get_object_url(),
            "absolute_url": self.adapter.get_absolute_url(),
            "object_name": self.adapter.object_name,
            "actor": self.adapter.actor,
            "actor_display": self.adapter.actor.get_display_name(),
            "actor_url": actor_url,
            "actor_absolute_url": self.adapter.community.resolve_url(actor_url),
            "recipient": self.adapter.recipient,
            "recipient_display": self.adapter.recipient.get_display_name(),
            "recipient_url": recipient_url,
            "recipient_absolute_url": self.adapter.community.resolve_url(recipient_url),
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

    def resolve(self, prefixes=None, suffix=".html"):
        """Generates list of standard Django template paths. Can
        be passed to loader.select_template() or similar.

        Pattern:
        {prefix}/{verb}_{object_name}{suffix}
        {prefix}/{verb}{suffix}
        {prefix}/{object_name}_notification{suffix}
        {prefix}/notification{suffix}

        Args:
            prefixes (List[str], optional): prefixes prepended to all the paths e.g. "post".
                (optional: None)
            suffix (str): suffix appended to all paths e.g. ".txt"

        Returns:
            list: list of path strs
        """
        return itertools.chain(
            [
                [
                    f"{prefix}/notifications/{self.verb}_{self.object_name}{suffix}",
                    f"{prefix}/notifications/{self.verb}{suffix}",
                    f"{prefix}/{self.object_name}_notification{suffix}",
                    f"{prefix}/notification{suffix}",
                ]
                for prefix in prefixes or [""]
            ]
        )


class TemplateRenderer:

    context_class = TemplateContext
    resolver_class = TemplateResolver

    def __init__(self, adapter, resolver=None, context=None):
        self.adapter = adapter
        self.resolver = resolver or self.resolver_class(self.adapter)
        self.context = context or self.context_class(self.adapter)

    def render(
        self, prefixes=None, suffix=".html", extra_context=None, template_engine=loader,
    ):
        """Renders a list of templates to a str. Use with TemplateResolver
        and TemplateContext.

        Args:
            extra_context (dict): template context
            template_engine (object, optional): Django template engine (default: loader)

        Returns:
            str: rendered template
        """
        return template_engine.render_to_string(
            self.resolver.resolve(prefixes, suffix),
            context=self.get_context(extra_context),
        )
