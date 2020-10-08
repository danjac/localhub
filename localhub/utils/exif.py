# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


class Exif:

    ROTATIONS = {3: 180, 6: 270, 8: 90}

    class Invalid(ValueError):
        ...

    @classmethod
    def from_image(cls, fp):
        """Returns Exif instance from file-like object

        Args:
            fp (file): file-like object containing an Image

        Returns:
            Exif

        Raises:
            Exif.Invalid: if image does not contain EXIF tags
        """
        img = Image.open(fp)

        if (exif := img._getexif()) is None:
            raise cls.Invalid("Image does not contain EXIF tags")

        return cls(img, exif)

    def __init__(self, image, exif):
        self.image = image
        self.exif = exif

    def rotate(self):
        """Attempt to rotate image based on EXIF orientation tags.

        Raises:
            Exif.Invalid: if data does not contain orientation tags.
        """

        self.image.seek(0)

        orientation = None

        for key in TAGS.keys():
            if TAGS[key] == "Orientation":
                orientation = key
                break

        if orientation is None or orientation not in self.ROTATIONS:
            raise self.Invalid("Cannot find valid orientation key")

        self.image.rotate(self.ROTATIONS[orientation], expand=True)

    def locate(self):
        """Returns lat, lng pair of coordinates.

        Returns:
            tuple(float, float): lat, lng coordinates

        Raises:
            Exif.Invalid: if EXIF data does not contain valid GPS data.
        """
        gps_dict = self.build_gps_dict()

        lat = self.convert_to_degress(gps_dict["GPSLatitude"])
        lng = self.convert_to_degress(gps_dict["GPSLongitude"])

        if gps_dict["GPSLatitudeRef"] != "N":
            lat = 0 - lat

        if gps_dict["GPSLongitudeRef"] != "E":
            lng = 0 - lng

        return lat, lng

    def convert_to_degress(self, value):
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
        except (IndexError, ValueError, TypeError, ZeroDivisionError):
            raise self.Invalid(f"Unable to convert to degress:{value}")

    def build_gps_dict(self):
        raw_values = {}
        for tag, value in self.exif.items():
            if TAGS.get(tag, tag) == "GPSInfo":
                raw_values = value

        if not raw_values:
            raise self.Invalid("GPSInfo not found in exif")

        gps_dict = {GPSTAGS.get(tag, tag): raw_values[tag] for tag in raw_values}

        # validation

        missing_keys = [
            key
            for key in (
                "GPSLatitudeRef",
                "GPSLongitudeRef",
                "GPSLatitude",
                "GPSLongitude",
            )
            if key not in gps_dict
        ]

        if missing_keys:
            raise self.Invalid(f"{','.join(missing_keys)} missing from GPS dict")

        return gps_dict
