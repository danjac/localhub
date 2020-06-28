# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import mimetypes
import os
from urllib.parse import urlparse

# Django
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# Third Party Libraries
import requests

_urlvalidator = URLValidator()


IMAGE_EXTENSIONS = (
    ".bmp",
    ".gif",
    ".gifv",
    ".jpeg",
    ".jpg",
    ".pjpeg",
    ".png",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
)

AUDIO_EXTENSIONS = (
    ".aac",
    ".au",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".wav",
    ".webm",
    ".wma",
)


class URLResolver:
    """Handles additional URL functionality
    """

    class Invalid(ValidationError):
        ...

    @classmethod
    def from_url(cls, url, resolve=False):
        """Create new instance from a URL. Automatically resolves "true"
        URL based on HEAD and redirects.

        Args:
            url (str): a valid URL
            resolve (bool, optional): resolves URL from HEAD (default: False)

        Returns:
            URLResolver instance

        Raises:
            Invalid: if URL is invalid
        """
        if resolve:
            url = resolve_url(url)
        return cls(url)

    def __init__(self, url):
        self.url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if not is_url(value):
            raise self.Invalid(f"{value} is not a valid URL")
        self._url = value
        self.parts = urlparse(self._url)

    @property
    def extension(self):
        """Returns file extension (always lowercase)"""
        _, ext = os.path.splitext(self.filename.lower())
        return ext

    @property
    def is_https(self):
        """Checks if URL is SSL i.e. starts with https://

        Returns:
            bool
        """
        return self.parts.scheme == "https"

    @property
    def is_image(self):
        """Checks if URL points to an image.

        Args:
            url (str)

        Returns:
            bool
        """
        return self.extension in IMAGE_EXTENSIONS

    @property
    def is_audio(self):
        """Checks if URL points to an audio file.

        Args:
            url (str)

        Returns:
            bool
        """
        return self.extension in AUDIO_EXTENSIONS

    @property
    def media_type(self):
        """Returns file media type, if any"""

        media_type, _ = mimetypes.guess_type(self.url)
        return media_type

    @property
    def root(self):
        """Returns the root domain URL minus path etc. For example:
        http://google.com/abc/ -> http://google.com

        Returns:
            str or None: domain url or None if not a valid URL
        """
        return self.parts.scheme + "://" + self.parts.netloc

    @property
    def domain(self):
        """Returns domain of URL e.g. http://google.com -> google.com.

        If "www." is present it is removed e.g. www.google.com -> google.com.

        Returns:
            str or None: domain or None if not valid URL.
        """
        if (domain := self.parts.netloc).startswith("www."):
            domain = domain[4:]
        return domain

    @property
    def filename(self):
        """Last part of a url e.g. "https://imgur.com/some-image.gif" ->
        "some-image.gif".

        Returns:
            str or None: filename or None if not a valid url
        """
        return self.parts.path.split("/")[-1]


def is_https(url):
    """Checks if URL is SSL i.e. starts with https://

    Args:
        url (str)

    Returns:
        bool
    """
    try:
        return URLResolver.from_url(url).is_https
    except URLResolver.Invalid:
        return False


def is_image_url(url):
    """Checks if URL points to an image.

    Args:
        url (str)

    Returns:
        bool
    """
    try:
        return URLResolver(url).from_url(url).is_image
    except URLResolver.Invalid:
        return False


def is_audio_url(url):
    """Checks if URL points to an audio file.

    Args:
        url (str)

    Returns:
        bool
    """
    try:
        return URLResolver(url).from_url(url).is_audio
    except URLResolver.Invalid:
        return False


def get_root_url(url):
    """Returns the root domain URL minus path etc. For example:
    http://google.com/abc/ -> http://google.com

    Args:
        url (str)

    Returns:
        str: domain url
    """
    try:
        return URLResolver.from_url(url).root
    except URLResolver.Invalid:
        return None


def get_domain(url):
    """Returns domain of URL e.g. http://google.com -> google.com.

    If "www." is present it is removed e.g. www.google.com -> google.com.

    Args:
        url (str): valid URL

    Returns:
        str: domain
    """
    try:
        return URLResolver.from_url(url).domain
    except URLResolver.Invalid:
        return None


def get_filename(url):
    """
    Returns last part of a url e.g. "https://imgur.com/some-image.gif" ->
    "some-image.gif".

    Args:
        url (str)

    Returns:
        str or None: filename or None if not a valid URL
    """
    try:
        return URLResolver.from_url(url).filename
    except URLResolver.Invalid:
        return None


def get_media_type(url):
    """Returns media type from url

    Args:
        url (str)

    Returns:
        str or None
    """
    try:
        return URLResolver.from_url(url).media_type
    except URLResolver.Invalid:
        return None


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
        response.raise_for_status()
        if response.url:
            return response.url
    except requests.RequestException:
        pass
    return url


def is_url(url):
    """Checks if a value is a valid URL.

    Args:
        url (str)

    Returns:
        bool
    """
    if url is None:
        return False
    try:
        _urlvalidator(url)
        return True
    except ValidationError:
        return False
