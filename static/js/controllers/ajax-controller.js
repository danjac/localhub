// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static values = {
    url: String,
    redirect: String,
    confirm: String,
    replace: Boolean,
    remove: Boolean,
  };

  get(event) {
    this.sendAjax('GET', event);
  }

  post(event) {
    this.sendAjax('POST', event);
  }

  async sendAjax(method, event) {
    event.preventDefault();

    if (this.hasConfirmValue && !window.confirm(this.confirmValue)) {
      return;
    }

    const { currentTarget } = event;

    let url;

    if (this.hasUrlValue) {
      url = this.urlValue;
    } else {
      url =
        currentTarget.getAttribute(`data-${this.identifier}-url`) ||
        currentTarget.getAttribute('href');
    }

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

    // data-ajax-redirect-value: override the default
    // redirect passed from the server. If set to "none" it
    // means "do not redirect at all".
    if (this.hasRedirectValue) {
      if (this.redirectValue !== 'none') Turbolinks.visit(this.redirectValue);
      return;
    }

    // data-ajax-replace-value: replace HTML in element with server HTML
    if (this.hasReplaceValue) {
      this.element.innerHTML = response.data;
      return;
    }

    // data-ajax-remove-value: remove element from DOM
    if (this.hasRemoveValue) {
      this.element.remove();
      return;
    }

    // default behaviour: redirect passed down in header
    if (response.headers['content-type'].match(/javascript/)) {
      /* eslint-disable-next-line no-eval */
      eval(response.data);
    }
  }
}
