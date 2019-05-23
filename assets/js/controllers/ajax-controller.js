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
    const referrer = location.href;

    const url = this.data.get('url');
    const redirect = this.data.get('redirect');

    axios({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      if (this.data.has('replace')) {
        this.element.innerHTML = response.data;
      } else if (redirect) {
        Turbolinks.visit(redirect);
      } else if (response.headers['content-type'].match(/javascript/)) {
        /* eslint-disable-next-line no-eval */
        eval(response.data);
      }
    });
  }
}
