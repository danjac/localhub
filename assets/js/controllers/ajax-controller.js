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
    const url = this.data.get('url') || this.element.getAttribute('href');

    this.element.setAttribute('disabled', true);

    axios({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    })
      .then(response => {

        const toggle = this.data.get('toggle');
        const redirect = this.data.get('redirect');

        if (toggle !== null) {
          this.element.classList.toggle('d-hide');
          this.element.removeAttribute('disabled');
          const target = toggle && document.querySelector(toggle);
          if (target) {
            target.classList.toggle('d-hide');
          }
        } else if (this.data.has('replace')) {
          this.element.innerHTML = response.data;
          this.element.removeAttribute('disabled');
        } else if (redirect) {
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
