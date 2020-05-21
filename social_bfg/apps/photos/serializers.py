# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Third Party Libraries
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.templatetags.thumbnail import is_portrait

# Social-BFG
from social_bfg.apps.activities.serializers import ActivitySerializer

# Local
from .models import Photo


class PhotoSerializer(ActivitySerializer):
    small_image_url = serializers.SerializerMethodField()
    large_image_url = serializers.SerializerMethodField()

    class Meta(ActivitySerializer.Meta):
        model = Photo
        fields = ActivitySerializer.Meta.fields + (
            "image",
            "latitude",
            "longitude",
            "artist",
            "original_url",
            "cc_license",
            "small_image_url",
            "large_image_url",
        )

    def _get_thumbnail_url(self, obj, size, **kwargs):
        return get_thumbnail(obj.image, size, upscale=False, **kwargs).url

    def get_small_image_url(self, obj):
        if is_portrait(obj.image):
            return self._get_thumbnail_url(obj, "500x300", crop="top")
        return self._get_thumbnail_url(obj, "500")

    def get_large_image_url(self, obj):
        return self._get_thumbnail_url(obj, "1000")
