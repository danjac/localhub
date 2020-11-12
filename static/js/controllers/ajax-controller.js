// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  get(event) {
    this.dispatch('GET', event);
  }

  post(event) {
    this.dispatch('POST', event);
  }

  async dispatch(method, event) {
    event.preventDefault();

    if (this.data.has('confirm') && !window.confirm(this.data.get('confirm'))) {
      return;
    }

    const { currentTarget } = event;

    const url =
      this.data.get('url') ||
      currentTarget.getAttribute(`data-${this.identifier}-url`) ||
      currentTarget.getAttribute('href');

    try {
      const response = await axios({
        headers: {
          'Turbolinks-Referrer': location.href,
        },
        method,
        url,
      });
      this.handleResponse(response);
    } catch (err) {
      if (err.response) {
        const { status, statusText } = err.response;
        this.toaster.error(`${status}: ${statusText}`);
      }
    }
  }

  handleResponse(response) {
    // success message passed from server
    const successMessage = response.headers['x-success-message'];

    if (successMessage) {
      this.toaster.success(successMessage);
    }

    // data-ajax-redirect: override the default
    // redirect passed from the server. If set to "none" it
    // means "do not redirect at all".
    const redirect = this.data.get('redirect');
    if (redirect) {
      if (redirect !== 'none') Turbolinks.visit(redirect);
      return;
    }

    // data-ajax-replace: replace HTML in element with server HTML
    if (this.data.has('replace')) {
      this.element.innerHTML = response.data;
      return;
    }

    // data-ajax-remove: remove element from DOM
    if (this.data.has('remove')) {
      this.element.remove();
      return;
    }

    // default behaviour: redirect passed down in header
    if (!redirect && response.headers['content-type'].match(/javascript/)) {
      /* eslint-disable-next-line no-eval */
      eval(response.data);
    }
  }
}
