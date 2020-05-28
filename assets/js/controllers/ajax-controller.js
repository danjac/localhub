// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Events } from '@/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['button'];

  get(event) {
    this.confirm('GET', event);
  }

  post(event) {
    this.confirm('POST', event);
  }

  confirm(method, event) {
    event.preventDefault();

    const { currentTarget } = event;

    if (this.isFetching(currentTarget)) {
      return;
    }

    const header = this.data.get('confirm-header');
    const body = this.data.get('confirm-body');

    if (header && body) {
      this.bus.pub(Events.CONFIRM_OPEN, {
        body,
        header,
        onConfirm: () => this.dispatch(method, currentTarget),
      });
    } else {
      this.dispatch(method, currentTarget);
    }
  }

  dispatch(method, target) {
    if (this.isFetching(target)) {
      return;
    }

    const url =
      this.data.get('url') ||
      target.getAttribute(`data-${this.identifier}-url`) ||
      target.getAttribute('href');

    target.setAttribute('disabled', 'disabled');

    this.startFetching();

    axios({
      headers: {
        'Turbolinks-Referrer': location.href,
      },
      method,
      url,
    })
      .then((response) => {
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
        } else {
          // only disable fetching if no redirects
          this.stopFetching();
        }
      })
      .catch((err) => {
        if (err.response) {
          const { status, statusText } = err.response;
          this.toaster.error(`${status}: ${statusText}`);
        }
        this.stopFetching();
      })
      .finally(() => {
        target.removeAttribute('disabled');
      });
  }

  isFetching(target) {
    return target.hasAttribute('disabled') || this.data.has('fetching');
  }

  startFetching() {
    this.data.set('fetching', true);
    if (this.buttonTargets.length) {
      Array.from(this.buttonTargets).forEach((btn) =>
        btn.setAttribute('disabled', 'disabled')
      );
    } else {
      this.element.setAttribute('disabled', 'disabled');
    }
  }

  stopFetching() {
    this.data.delete('fetching');
    if (this.buttonTargets.length) {
      Array.from(this.buttonTargets).forEach((btn) => btn.removeAttribute('disabled'));
    } else {
      this.element.removeAttribute('disabled');
    }
  }
}
