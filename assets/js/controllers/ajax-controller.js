// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  // handles simple non-form AJAX interactions
  get(event) {
    this.send('GET', event);
  }

  post(event) {
    this.send('POST', event);
  }

  delete(event) {
    this.send('DELETE', event);
  }

  put(event) {
    this.send('PUT', event);
  }

  patch(event) {
    this.send('PATCH', event);
  }

  send(method, event) {
    event.preventDefault();

    // anchor doesn't have disabled attr, we'll simulate here
    if (this.element.hasAttribute('disabled')) {
      return;
    }

    this.element.setAttribute('disabled', 'disabled');

    const referrer = location.href;
    const url = this.element.getAttribute('href');

    axios({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    })
      .then(response => {
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
