# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.activities.serializers import ActivitySerializer

# Local
from .models import Post


class PostSerializer(ActivitySerializer):

    domain = serializers.SerializerMethodField()
    base_url = serializers.SerializerMethodField()

    class Meta(ActivitySerializer.Meta):
        model = Post
        fields = ActivitySerializer.Meta.fields + (
            "url",
            "base_url",
            "opengraph_image",
            "opengraph_description",
            "domain",
        )
        api_basename = "/api/posts/"

    def get_domain(self, obj):
        return obj.get_domain()

    def get_base_url(self, obj):
        return obj.get_base_url()
