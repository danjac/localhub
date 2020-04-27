# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import View

from localhub.utils.http import URLResolver
from localhub.utils.scraper import HTMLScraper


class OpengraphPreviewView(View):
    """
    Does opengraph preview of URL.

    Returns JSON:
    {
        "title"
        "image"
        "description"
    }
    """

    def get(self, request):
        try:
            url_resolver = URLResolver.from_url(request.GET["url"], resolve=True)
            if url_resolver.is_image:
                data = {
                    "title": url_resolver.filename,
                    "image": url_resolver.url,
                    "description": "",
                }
            else:
                scraper = HTMLScraper.from_url(url_resolver.url)
                data = {
                    "title": (scraper.title or "")[:300],
                    "image": scraper.image,
                    "description": scraper.description,
                }
            return JsonResponse(data)

        except KeyError:
            return self.handle_bad_request(_("No URL provided"))
        except URLResolver.Invalid:
            return self.handle_bad_request(_("Invalid or inaccessible URL"))
        except HTMLScraper.Invalid:
            return self.handle_bad_request(_("Unable to fetch meta content from page"))

    def handle_bad_request(self, error):
        return HttpResponseBadRequest(error)


opengraph_preview_view = OpengraphPreviewView.as_view()
