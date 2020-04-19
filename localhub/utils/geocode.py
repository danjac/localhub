# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

import geopy

geolocator = geopy.Nominatim(user_agent=settings.LOCALHUB_GEOLOCATOR_USER_AGENT)


def geocode(street_address=None, locality=None, postal_code=None, country=None):
    """Fetches the lat/lng coordinates from Open Street Map API.

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
    result = geolocator.geocode(q)
    if result:
        return result.latitude, result.longitude
    return None, None
