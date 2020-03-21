# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import io

import pytest
from django.core.files import File
from PIL import Image

from ..factories import PhotoFactory


@pytest.fixture
def photo_for_member(member):
    return PhotoFactory(owner=member.member, community=member.community)


@pytest.fixture
def fake_image():
    file_obj = io.BytesIO()
    image = Image.new("RGBA", size=(500, 500), color="blue")
    image.save(file_obj, "png")
    file_obj.seek(0)
    return File(file_obj, name="test.jpg")
