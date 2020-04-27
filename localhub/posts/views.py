# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseBadRequest, JsonResponse
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
                return JsonResponse(
                    {
                        "title": url_resolver.filename,
                        "image": url_resolver.url,
                        "description": "",
                    }
                )
            scraper = HTMLScraper.from_url(url_resolver.url)
        except KeyError:
            return HttpResponseBadRequest("No URL provided")
        except URLResolver.Invalid:
            return HttpResponseBadRequest("Invalid or inaccessible URL")
        except HTMLScraper.Invalid:
            return HttpResponseBadRequest("Unable to fetch meta content from page")

        return JsonResponse(
            {
                "title": scraper.title,
                "image": scraper.image,
                "description": scraper.description,
            }
        )


opengraph_preview_view = OpengraphPreviewView.as_view()
