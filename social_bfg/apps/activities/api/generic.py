# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.db import IntegrityError
from django.utils import timezone

# Django Rest Framework
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# Social-BFG
from social_bfg.apps.bookmarks.models import Bookmark
from social_bfg.apps.comments.serializers import CommentSerializer
from social_bfg.apps.communities.permissions import (
    IsCommunityMember,
    IsCommunityModerator,
)
from social_bfg.apps.likes.models import Like

# Local
from ..permissions import IsActivityOwner, IsCommentAllowed, IsNotActivityOwner
from ..utils import get_activity_models


class ActivityViewSet(ModelViewSet):
    permission_classes = [
        IsCommunityMember,
        IsActivityOwner,
    ]

    def get_queryset(self):
        return (
            self.model.objects.for_community(self.request.community)
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
            .select_related("owner", "editor", "parent__owner")
            .order_by("-published", "-created")
        )

    # TBD: moderator delete should be a dedicated endpoint.

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            community=self.request.community,
            published=timezone.now() if self.request.data.get("publish") else None,
        )
        if serializer.instance.published:
            serializer.instance.notify_on_publish()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        obj = self.get_object()
        if not obj.published:
            obj.published = timezone.now()
            obj.save()
            obj.notify_on_publish()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCommunityMember, IsNotActivityOwner],
    )
    def like(self, request, pk=None):

        obj = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=obj.owner,
                content_object=obj,
            ).notify()

        except IntegrityError:
            # dupe, ignore
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsCommunityMember, IsNotActivityOwner],
    )
    def dislike(self, request, pk=None):
        self.get_object().get_likes().filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsCommunityMember])
    def add_bookmark(self, request, pk=None):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.get_object(),
            )
        except IntegrityError:
            # dupe, ignore
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["delete"], permission_classes=[IsCommunityMember])
    def remove_bookmark(self, request, pk=None):
        self.get_object().get_bookmarks().filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCommunityMember, IsCommentAllowed],
    )
    def add_comment(self, request, pk=None):
        obj = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(
                owner=request.user, community=request.community, content_object=obj,
            )

            comment.notify_on_create()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsCommunityModerator])
    def pin(self, request, pk=None):
        # TBD: we need either an endpoint to get the "pinned" object, or just include
        # with initial JSON load.
        obj = self.get_object()
        # unpin any others
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        obj.is_pinned = True
        obj.save()
        # TBD: these actions should all be HTTP_204_NO_CONTENT
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["delete"], permission_classes=[IsCommunityModerator])
    def unpin(self, request, pk=None):
        obj = self.get_object()
        obj.is_pinned = False
        obj.save()
        # TBD: these actions should all be HTTP_204_NO_CONTENT
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        # TBD: should be paginated
        comments = (
            self.get_object()
            .get_comments()
            .for_community(self.request.community)
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_deleted()
            .with_common_related()
            .order_by("created")
        )
        return Response(CommentSerializer(comments, many=True).data)
