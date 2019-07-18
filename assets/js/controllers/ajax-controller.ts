// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios, { AxiosResponse, Method } from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  // handles simple non-form AJAX interactions
  get(event: Event) {
    this.send('GET', event);
  }

  post(event: Event) {
    this.send('POST', event);
  }

  delete(event: Event) {
    this.send('DELETE', event);
  }

  put(event: Event) {
    this.send('PUT', event);
  }

  patch(event: Event) {
    this.send('PATCH', event);
  }

  send(method: Method, event: Event) {
    event.preventDefault();

    const referrer = location.href;
    const url = this.data.get('url') || this.element.getAttribute('href');

    axios.request({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then((response: AxiosResponse) => {
      const toggle = this.data.get('toggle');
      const redirect = this.data.get('redirect');

      if (toggle !== null) {
        this.element.classList.toggle('d-hide');
        const target = toggle && document.querySelector(toggle);
        if (target) {
          target.classList.toggle('d-hide');
        }
      } else if (this.data.has('replace')) {
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
