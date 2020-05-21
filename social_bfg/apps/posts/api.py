# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Social-BFG
from social_bfg.apps.activities.views.api import ActivityViewSet

# Local
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ActivityViewSet):
    model = Post
    serializer_class = PostSerializer
