# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.exceptions import ValidationError

# Third Party Libraries
import pytest

from ..validators import validate_hashtags


class TestValidateHashtags:
    def test_none(self):
        validate_hashtags(None)

    def test_empty(self):
        validate_hashtags("")

    def test_valid_single_tag(self):
        validate_hashtags("#wallpapers")

    def test_invalid_single_tag(self):
        with pytest.raises(ValidationError):
            validate_hashtags("wallpapers")

    def test_valid_single_tag_with_spaces(self):
        validate_hashtags("   #wallpapers    ")

    def test_multiple_tags(self):
        validate_hashtags("#wallpapers #photography #monochrome")

    def test_invalid_tag_in_many(self):
        with pytest.raises(ValidationError):
            validate_hashtags("#wallpapers photography #monochrome")
