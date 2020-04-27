// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* global require */
import axios from 'axios';
import Turbolinks from 'turbolinks';
import hoverintent from 'hoverintent';

import { Application } from 'stimulus';
import { definitionsFromContext } from 'stimulus/webpack-helpers';

// Axios setup
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// Stimulus setup
const application = Application.start();
const context = require.context('./controllers', true, /\.js$/);
application.load(definitionsFromContext(context));

// instant click setup

document.addEventListener('turbolinks:load', () => {
  document.querySelectorAll('a').forEach((el) => {
    // TBD: all those AJAX <a> elements should be data-turbolinks="false"
    if (el.dataset.turbolinks === 'false' || el.dataset.controller === 'ajax') {
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
          prefetcher = document.body.appendChild(link);
        }
      },
      () => {},
      {
        options: 50,
        sensitivity: 5,
      }
    );
  });
});

// Turbolinks setup
Turbolinks.start();
