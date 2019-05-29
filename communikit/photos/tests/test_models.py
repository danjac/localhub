# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.utils.encoding import force_str

from communikit.communities.models import Community, Membership
from communikit.photos.models import Photo
from communikit.photos.tests.factories import PhotoFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPhotoModel:
    def test_breadcrumbs(self, photo: Photo):
        assert photo.get_breadcrumbs() == [
            ("/", "Home"),
            ("/photos/", "Photos"),
            (f"/photos/{photo.id}/", force_str(photo.title)),
        ]

    def test_notify(self, community: Community):
        owner = UserFactory(username="owner")
        moderator = UserFactory()

        Membership.objects.create(
            member=owner, community=community, role=Membership.ROLES.moderator
        )
        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )

        photo = PhotoFactory(
            owner=owner,
            community=community,
        )
        notifications = photo.notify(created=True)

        assert notifications[0].recipient == moderator
        assert notifications[0].verb == "created"

        # ensure saved to db
        assert photo.notifications.count() == 1

        # change the description and remove the mention
        photo.description = "hello!"
        photo.save()

        notifications = photo.notify(created=False)

        assert notifications[0].recipient == moderator
        assert notifications[0].verb == "updated"

        assert photo.notifications.count() == 2
