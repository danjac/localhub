# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


class InvalidExifData(ValueError):
    ...


def get_geolocation_data_from_image(fp):
    """
    Extracts lat, lng tuple from image file object.

    If invalid raises InvalidExifData exception.
    """
    img = Image.open(fp)

    exif = img._getexif()
    if exif is None:
        raise InvalidExifData("No exif data found")

    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            return extract_gps_data(value)
    raise InvalidExifData("No GPS data foudn")


def convert_to_degress(value):
    """
    Convert GPS coordinate to degress in float
    """
    print(value)
    d0 = value[0][0]
    d1 = value[0][1]

    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]

    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]

    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def build_gps_data(value):
    return {GPSTAGS.get(tag, tag): value[tag] for tag in value}


def extract_gps_data(value):
    gps_data = build_gps_data(value)

    lat = gps_data.get("GPSLatitude")
    lng = gps_data.get("GPSLongitude")
    lat_ref = gps_data.get("GPSLatitudeRef")
    lng_ref = gps_data.get("GPSLongitudeRef")

    if not all((lat, lng, lat_ref, lng_ref)):
        raise InvalidExifData(
            "Missing lat/lng datai %r, %r, %r, %r" % (lat, lng, lat_ref, lng_ref)
        )
        return None, None

    try:
        lat = convert_to_degress(lat)
        lng = convert_to_degress(lng)
    except IndexError:
        raise InvalidExifData("Unable to convert to digress: %r, %r" % (lat, lng))

    if lat_ref != "N":
        lat = 0 - lat

    if lng_ref != "E":
        lng = 0 - lng

    return lat, lng
