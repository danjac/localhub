// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Events } from '~/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  get(event) {
    this.confirm('GET', event);
  }

  post(event) {
    this.confirm('POST', event);
  }

  confirm(method, event) {
    event.preventDefault();

    const { currentTarget } = event;

    const header = this.data.get('confirm-header');
    const body = this.data.get('confirm-body');

    const handleDispatch = () => this.dispatch(method, currentTarget);

    if (header && body) {
      this.bus.pub(Events.CONFIRM_OPEN, {
        body,
        header,
        onConfirm: handleDispatch,
      });
    } else {
      handleDispatch();
    }
  }

  async dispatch(method, target) {
    const url =
      this.data.get('url') ||
      target.getAttribute(`data-${this.identifier}-url`) ||
      target.getAttribute('href');

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
