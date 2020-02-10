# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


def darkmode(request):
    return {"darkmode": "darkmode" in request.COOKIES}
