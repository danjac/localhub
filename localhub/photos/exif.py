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
        raise InvalidExifData("Image does not contain EXIF tags")

    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            return extract_gps_data(value)
    raise InvalidExifData("No GPS data found in EXIF tags")


def convert_to_degress(value):
    """
    Convert GPS coordinate to degress in float
    """
    try:
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
    except (IndexError, ValueError, ZeroDivisionError):
        raise InvalidExifData(f"Unable to convert to digress:{value}")


def build_gps_data(value):
    return {GPSTAGS.get(tag, tag): value[tag] for tag in value}


def get_gps_data_point(gps_data, key):
    try:
        return gps_data[key]
    except KeyError:
        raise InvalidExifData(f"{key} missing from GPS EXIF data")


def extract_gps_data(value):
    gps_data = build_gps_data(value)

    lat_ref = get_gps_data_point(gps_data, "GPSLatitudeRef")
    lng_ref = get_gps_data_point(gps_data, "GPSLongitudeRef")

    lat = convert_to_degress(get_gps_data_point(gps_data, "GPSLatitude"))
    lng = convert_to_degress(get_gps_data_point(gps_data, "GPSLongitude"))

    if lat_ref != "N":
        lat = 0 - lat

    if lng_ref != "E":
        lng = 0 - lng

    return lat, lng
