# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings

# Third Party Libraries
import geopy

geolocator = geopy.Nominatim(user_agent=settings.GEOLOCATOR_USER_AGENT)


def geocode(street_address=None, locality=None, postal_code=None, country=None):
    """Fetches the lat/lng coordinates from Open Street Map API.

    Args:
        street_address (str, optional) (default: None)
        locality (str, optional) (default: None)
        postal_code (str, optional) (default: None)
        country (str, optional): country code e.g. "FI" (default: None)

    Returns:
        tuple: lat/lng pair. These will be float or None if
            no location can be found.
    """
    q = {
        "street": street_address,
        "postalcode": postal_code,
        "city": locality,
        "country": country,
    }
    if not all(q.values()):
        return None, None
    if result := geolocator.geocode(q):
        return result.latitude, result.longitude
    return None, None
