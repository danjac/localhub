# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer
from social_bfg.serializers import GenericObjectSerializer

# Local
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Base class for all activity serializers."""

    owner = UserSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    markdown = serializers.SerializerMethodField()

    content_object = serializers.SerializerMethodField()

    # annotated fields

    num_likes = serializers.IntegerField(read_only=True)

    is_flagged = serializers.BooleanField(read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    has_bookmarked = serializers.BooleanField(read_only=True)
    has_flagged = serializers.BooleanField(read_only=True)
    has_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment

        fields = (
            "id",
            "content",
            "markdown",
            "content_object",
            "owner",
            # editor,
            "parent",
            "created",
            "edited",
            "is_new",
            "is_flagged",
            "num_likes",
            "has_bookmarked",
            "has_flagged",
            "has_liked",
        )

        read_only_fields = ("edited",)

    def get_content_object(self, obj):
        if obj.content_object is None:
            return None
        # this should prob. be a "generic serializer" that just
        # renders __str__ instead of title.
        return GenericObjectSerializer(obj.content_object).data

    def get_markdown(self, obj):
        return obj.content.markdown()
