# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.utils.translation import gettext as _

# Localhub
from localhub.common.utils.http import URLResolver
from localhub.common.utils.scraper import HTMLScraper


def opengraph_preview_view(request):

    try:
        return fetch_preview_data(request.GET["url"])
    except KeyError:
        return HttpResponseBadRequest(_("No URL provided"))
    except URLResolver.Invalid:
        return HttpResponseBadRequest(_("Invalid or inaccessible URL"))
    except HTMLScraper.Invalid:
        return HttpResponseBadRequest(_("Unable to fetch meta content from page"))


def render_preview_data(url, title, image, description):
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


def fetch_preview_data(url):
    url_resolver = URLResolver.from_url(url, resolve=True)
    if url_resolver.is_image:
        return render_preview_data(
            url=url_resolver.url,
            title=url_resolver.filename,
            image=url_resolver.url,
            description="",
        )

    scraper = HTMLScraper.from_url(url_resolver.url)

    return render_preview_data(
        url=scraper.url,
        title=(scraper.title or "")[:300],
        image=scraper.image,
        description=scraper.description,
    )
