# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localite.communities.models import Community, Membership
from localite.photos.models import Photo
from localite.photos.tests.factories import PhotoFactory
from localite.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPhotoModel:
    def test_breadcrumbs(self, photo: Photo):
        breadcrumbs = photo.get_breadcrumbs()
        assert len(breadcrumbs) == 3
        assert breadcrumbs[2][0] == photo.get_absolute_url()

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

        photo = PhotoFactory(owner=owner, community=community)
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
