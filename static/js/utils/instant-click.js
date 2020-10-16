// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Instant click setup

//https://github.com/turbolinks/turbolinks/issues/313#issuecomment-395819000

import hoverintent from 'hoverintent';

export default function instantClick(interval = 50, sensitivity = 5) {
  document.addEventListener('turbolinks:load', () => {
    document.querySelectorAll('a').forEach((el) => {
      if (el.dataset.turbolinks === 'false') {
        return;
      }

      let prefetcher;
      hoverintent(
        el,
        () => {
          const href = el.getAttribute('href');
          if (!href.match(/^\//)) {
            return;
          }
          if (prefetcher) {
            if (prefetcher.getAttribute('href') !== href) {
              prefetcher.setAttribute('href', href);
            }
          } else {
            const link = document.createElement('link');
            link.setAttribute('rel', 'prefetch');
            link.setAttribute('href', href);
            prefetcher = document.head.appendChild(link);
          }
        },
        () => {},
        {
          interval,
          sensitivity,
        }
      );
    });
  });
}
