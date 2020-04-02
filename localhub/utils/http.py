# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from urllib.parse import urlparse

import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_urlvalidator = URLValidator()


IMAGE_EXTENSIONS = (
    "bmp",
    "gif",
    "gifv",
    "jpeg",
    "jpg",
    "pjpeg",
    "png",
    "svg",
    "tif",
    "tiff",
    "webp",
)


class URLResolver:
    """Handles additional URL functionality
    """

    @classmethod
    def from_url(cls, url):
        """Create new instance from a URL. Automatically resolves "true"
        URL based on HEAD and redirects.

        Args:
            url (str): a valid URL

        Returns:
            URLResolver instance
        """
        return cls(resolve_url(url))

    def __init__(self, url):
        self.url = url

    def __bool__(self):
        return self.is_valid

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url
        if self._url is None:
            self.is_valid = False
        else:
            try:
                _urlvalidator(self._url)
                self.is_valid = True
                self._parts = urlparse(self.url)
            except ValidationError:
                self.is_valid = False

    @property
    def is_https(self):
        """Checks if URL is SSL i.e. starts with https://

        Returns:
            bool
        """
        return self.is_valid and self._parts.scheme == "https"

    @property
    def is_image(self):
        """Checks if URL points to an image.

        Args:
            url (str)

        Returns:
            bool
        """
        if not self.is_valid:
            return False
        _, ext = os.path.splitext(self._parts.path.lower())
        return ext[1:] in IMAGE_EXTENSIONS

    @property
    def root(self):
        """Returns the root domain URL minus path etc. For example:
        http://google.com/abc/ -> http://google.com

        Returns:
            str or None: domain url or None if not a valid URL
        """

        if not self.is_valid:
            return None
        return self._parts.scheme + "://" + self._parts.netloc

    @property
    def domain(self):
        """Returns domain of URL e.g. http://google.com -> google.com.

        If "www." is present it is removed e.g. www.google.com -> google.com.

        Returns:
            str or None: domain or None if not valid URL.
        """
        if not self.is_valid:
            return None

        domain = self._parts.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    @property
    def filename(self):
        """Last part of a url e.g. "https://imgur.com/some-image.gif" ->
        "some-image.gif".

        Returns:
            str or None: filename or None if not a valid url
        """

        if not self.is_valid:
            return None
        return self._parts.path.split("/")[-1]


def is_https(url):
    """Checks if URL is SSL i.e. starts with https://

    Args:
        url (str)

    Returns:
        bool
    """
    return URLResolver(url).is_https


def is_url(url):
    """Checks if a value is a valid URL.

    Args:
        url (str)

    Returns:
        bool
    """
    return URLResolver(url).is_valid


def is_image_url(url):
    """Checks if URL points to an image.

    Args:
        url (str)

    Returns:
        bool
    """
    return URLResolver(url).is_image


def get_root_url(url):
    """Returns the root domain URL minus path etc. For example:
    http://google.com/abc/ -> http://google.com

    Args:
        url (str)

    Returns:
        str: domain url
    """
    return URLResolver(url).root


def get_domain(url):
    """Returns domain of URL e.g. http://google.com -> google.com.

    If "www." is present it is removed e.g. www.google.com -> google.com.

    Args:
        url (str): valid URL

    Returns:
        str: domain
    """
    return URLResolver(url).domain


def get_filename(url):
    """
    Returns last part of a url e.g. "https://imgur.com/some-image.gif" ->
    "some-image.gif".
    """
    return URLResolver(url).filename


def resolve_url(url):
    """Resolves URL from HEAD and redirects to get the "true" URL.

    Args:
        url (str)

    Returns:
        str: URL. If no HEAD found then returns original URL.
    """
    if not url:
        return url

    try:
        response = requests.head(url, allow_redirects=True)
        if response.ok and response.url:
            return response.url
    except (requests.RequestException):
        pass
    return url
