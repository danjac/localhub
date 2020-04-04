// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  /*
  Handles non-form AJAX interactions.

  actions:
    get: HTTP GET request
    post: HTTP POST request
    delete: HTTP DELETE request
    put: HTTP PUT request
    patch: HTTP PATCH request

  data:
    url: location of AJAX endpoint. If element has "href" attribute this can
      be used instead.
    redirect: location of redirect on successful completion. This overrides any
      Location returned from the server. If "none" will not perform any redirect.
  */
  get(event) {
    this.dispatch('GET', event);
  }

  post(event) {
    this.dispatch('POST', event);
  }

  delete(event) {
    this.dispatch('DELETE', event);
  }

  put(event) {
    this.dispatch('PUT', event);
  }

  patch(event) {
    this.dispatch('PATCH', event);
  }

  dispatch(method, event) {
    event.preventDefault();

    // anchor doesn't have disabled attr, we'll simulate here
    if (this.element.hasAttribute('disabled')) {
      return;
    }

    this.element.setAttribute('disabled', 'disabled');

    const referrer = location.href;
    const url = this.element.getAttribute('href') || this.data.get('url');

    axios({
      headers: {
        'Turbolinks-Referrer': referrer,
      },
      method,
      url,
    })
      .then((response) => {
        const redirect = this.data.get('redirect');
        if (redirect === 'none') {
          this.element.removeAttribute('disabled');
          return;
        }

        if (redirect) {
          Turbolinks.visit(redirect);
        } else if (response.headers['content-type'].match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }
      })
      .catch(() => {
        this.element.removeAttribute('disabled');
      });
  }
}
