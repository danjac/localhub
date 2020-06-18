# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template

register = template.Library()


@register.inclusion_tag("posts/includes/opengraph.html")
def render_opengraph_content(user, post):
    """Returns OG and other meta external content depending on individual post and user preferences.

    Args:
        user (User): authenticated user
        post (Post)

    Returns:
        dict or None: if no content or URL then returns None. Otherwise returns dict of "image" and
            "description".
    """

    if not post.url or (not post.opengraph_description and not post.opengraph_image):
        return {
            "post": post,
            "og_data": None,
        }

    opengraph_data = {
        "description": post.opengraph_description,
        "image": "",
    }

    if user.is_anonymous or user.show_external_images:
        opengraph_data["image"] = post.get_opengraph_image_if_safe()

    return {"og_data": opengraph_data, "post": post}
