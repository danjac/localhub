# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.template import loader


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
