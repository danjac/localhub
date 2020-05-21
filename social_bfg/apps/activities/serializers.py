# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer


class ActivitySerializer(serializers.ModelSerializer):
    """Base class for all activity serializers."""

    owner = UserSerializer(read_only=True)

    # annotated fields

    num_likes = serializers.IntegerField(read_only=True)
    num_comments = serializers.IntegerField(read_only=True)
    num_reshares = serializers.IntegerField(read_only=True)

    is_flagged = serializers.BooleanField(read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    has_bookmarked = serializers.BooleanField(read_only=True)
    has_liked = serializers.BooleanField(read_only=True)
    has_reshared = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            "id",
            "title",
            "hashtags",
            "mentions",
            "description",
            "allow_comments",
            "owner",
            "created",
            "updated",
        )
