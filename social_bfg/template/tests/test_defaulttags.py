# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template

from ..defaulttags import svg


class TestSvg:
    def test_svg(self):
        html = svg("x_circle")
        assert "<svg" in html
        assert 'class="text-black' in html

    def test_svg_white_variant(self):
        html = svg("x_circle", variant="white")
        assert "<svg" in html
        assert 'class="text-white' in html

    def test_svg_custom_css(self):
        html = svg("x_circle", css_class="text-gray-500")
        assert "<svg" in html
        assert 'class="text-gray-500' in html


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
