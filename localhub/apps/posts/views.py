# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.utils.translation import gettext as _
from django.views.generic import View

# Localhub
# Social-BFG
from localhub.utils.http import URLResolver
from localhub.utils.scraper import HTMLScraper


class OpengraphPreviewView(View):
    """
    Does opengraph preview of URL.

    """

    def get(self, request):
        try:
            return self.fetch_preview_data(request.GET["url"])
        except KeyError:
            return self.handle_bad_request(_("No URL provided"))
        except URLResolver.Invalid:
            return self.handle_bad_request(_("Invalid or inaccessible URL"))
        except HTMLScraper.Invalid:
            return self.handle_bad_request(_("Unable to fetch meta content from page"))

    def render_preview_data(self, url, title, image, description):
        return JsonResponse(
            {
                "fields": {
                    "url": url,
                    "title": title,
                    "opengraph_image": image,
                    "opengraph_description": description,
                },
                "html": loader.render_to_string(
                    "posts/includes/opengraph_preview.html",
                    {
                        "preview": {
                            "title": title,
                            "image": image,
                            "description": description,
                        }
                    },
                ),
            }
        )

    def fetch_preview_data(self, url):
        url_resolver = URLResolver.from_url(url, resolve=True)
        if url_resolver.is_image:
            return self.render_preview_data(
                url=url_resolver.url,
                title=url_resolver.filename,
                image=url_resolver.url,
                description="",
            )

        scraper = HTMLScraper.from_url(url_resolver.url)

        return self.render_preview_data(
            url=scraper.url,
            title=(scraper.title or "")[:300],
            image=scraper.image,
            description=scraper.description,
        )

    def handle_bad_request(self, error):
        return HttpResponseBadRequest(error)


opengraph_preview_view = OpengraphPreviewView.as_view()
