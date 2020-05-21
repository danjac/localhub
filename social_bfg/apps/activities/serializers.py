# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer


class RelatedActivitySerializer(serializers.Serializer):
    """For use as generic content object. We can't use
    a ModelSerializer as that doesn't work with abstract models.
    """

    id = serializers.IntegerField()
    title = serializers.CharField()
    object_name = serializers.SerializerMethodField()

    def get_object_name(self, obj):
        return obj._meta.model_name


class ActivitySerializer(serializers.ModelSerializer):
    """Base class for all activity serializers. Subclass
    for all supported models."""

    owner = UserSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    object_type = serializers.SerializerMethodField()

    # annotated fields

    num_likes = serializers.IntegerField(read_only=True)
    num_comments = serializers.IntegerField(read_only=True)
    num_reshares = serializers.IntegerField(read_only=True)

    is_flagged = serializers.BooleanField(read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    has_bookmarked = serializers.BooleanField(read_only=True)
    has_flagged = serializers.BooleanField(read_only=True)
    has_liked = serializers.BooleanField(read_only=True)
    has_reshared = serializers.BooleanField(read_only=True)

    markdown = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "title",
            "hashtags",
            "mentions",
            "description",
            "markdown",
            "allow_comments",
            "owner",
            "is_pinned",
            "is_reshare",
            "created",
            "edited",
            "published",
            "is_new",
            "is_flagged",
            "num_likes",
            "num_reshares",
            "num_comments",
            "has_bookmarked",
            "has_flagged",
            "has_liked",
            "has_reshared",
            "object_type",
        )

        read_only_fields = (
            "edited",
            "published",
            "is_reshare",
            "is_pinned",
        )

    def get_markdown(self, obj):
        return obj.description.markdown()

    def get_object_type(self, obj):
        return obj._meta.model_name
