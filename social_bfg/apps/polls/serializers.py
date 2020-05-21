# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.activities.serializers import ActivitySerializer

# Local
from .models import Answer, Poll


class AnswerSerializer(serializers.ModelSerializer):
    poll = serializers.PrimaryKeyRelatedField(read_only=True)
    voters = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    # annotated field
    num_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Answer
        fields = ("description", "poll", "voters", "num_votes")


class PollSerializer(ActivitySerializer):

    answers = AnswerSerializer(many=True, read_only=True)
    # total_num_votes = serializers.SerializerMethodField()

    class Meta(ActivitySerializer.Meta):
        model = Poll
        fields = ActivitySerializer.Meta.fields + (
            "allow_voting",
            # "total_num_votes",
            "answers",
        )

    def get_total_num_votes(self, obj):
        return obj.total_num_votes
