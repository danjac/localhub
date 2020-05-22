# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Social-BFG
from social_bfg.apps.activities.serializers import ActivitySerializer

# Local
from .models import Post


class PostSerializer(ActivitySerializer):
    class Meta(ActivitySerializer.Meta):
        model = Post
        fields = ActivitySerializer.Meta.fields + (
            "url",
            "opengraph_image",
            "opengraph_description",
        )
        api_basename = "/api/posts/"
