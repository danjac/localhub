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
    url: location of AJAX endpoint. If element has "href" attribute this
      can be used instead. This may also be placed on the action event target.
    redirect: location of redirect on successful completion. This overrides any
      Location returned from the server. If "none" will not perform any redirect.
  targets:
    fragment: if present and HTML is returned from endpoint the contents of this
      target will be replaced with the HTML.
  */
  static targets = ['fragment'];

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

    const { currentTarget } = event;

    if (currentTarget.hasAttribute('disabled')) {
      return;
    }

    const url =
      this.data.get('url') ||
      currentTarget.getAttribute(`data-${this.data.identifier}-url`) ||
      currentTarget.getAttribute('href');

    currentTarget.setAttribute('disabled', 'disabled');

    axios({
      headers: {
        'Turbolinks-Referrer': location.href,
      },
      method,
      url,
    })
      .then((response) => {
        if (this.hasFragmentTarget) {
          this.fragmentTarget.innerHTML = response.data;
          currentTarget.removeAttribute('disabled');
          return;
        }
        const redirect = this.data.get('redirect');
        if (redirect === 'none') {
          currentTarget.removeAttribute('disabled');
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
        currentTarget.removeAttribute('disabled');
      });
  }
}
