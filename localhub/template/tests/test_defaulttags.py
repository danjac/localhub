# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template


class TestCollapsable:
    def test_if_no_args(self):
        tmpl = template.Template(
            """
        {% collapsable %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({}))
        assert 'data-controller="collapsable"' in rendered

    def test_if_ignore_false(self):
        tmpl = template.Template(
            """
        {% collapsable ignore %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({"ignore": False}))
        assert 'data-controller="collapsable"' in rendered

    def test_if_ignore_true(self):
        tmpl = template.Template(
            """
        {% collapsable ignore %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({"ignore": True}))
        assert 'data-controller="collapsable"' not in rendered
