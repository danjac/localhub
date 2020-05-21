# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer

# Local
from .models import Community, Membership

# Note: this will be request.community. We probably want
# to add some way of handling current community with a header
# e.g. X-Community or something as well as session.


# Memberships: we want to be able to pull down the current
# membership for the user...prob. can do in immediate load.


class CommunitySerializer(serializers.ModelSerializer):
    """Maybe need separate serializer to accomodate list"""

    absolute_url = serializers.SerializerMethodField()

    description_markdown = serializers.SerializerMethodField()
    terms_markdown = serializers.SerializerMethodField()
    intro_markdown = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "logo",
            "tagline",
            "active",
            "public",
            "absolute_url",
            "allow_join_requests",
            "blacklisted_email_addresses",
            "blacklisted_email_domains",
            "content_warning_tags",
            "terms",
            "description",
            "description_markdown",
            "intro_markdown",
            "terms_markdown",
        )

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_description_markdown(self, obj):
        return obj.description.markdown()

    def get_intro_markdown(self, obj):
        return obj.intro.markdown()

    def get_terms_markdown(self, obj):
        return obj.terms.markdown()


class MembershipSerializer(serializers.ModelSerializer):
    """Current member role could be included in initial page load.

    We probably don't need the entire membership details.
    """

    # community = CommunitySerializer(read_only=True)
    member = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = (
            # "community",
            "member",
            "role",
            "active",
        )
