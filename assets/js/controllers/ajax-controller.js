// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Events } from '@utils/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['toggle', 'button'];

  connect() {
    this.bus.sub(Events.AJAX_FETCHING, () => this.data.set('fetching', true));
    this.bus.sub(Events.AJAX_COMPLETE, () => this.data.delete('fetching'));
  }

  get(event) {
    this.confirm('GET', event);
  }

  post(event) {
    this.confirm('POST', event);
  }

  confirm(method, event) {
    event.preventDefault();

    const { currentTarget } = event;

    if (currentTarget.hasAttribute('disabled') || this.data.has('fetching')) {
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
    if (target.hasAttribute('disabled') || this.data.has('fetching')) {
      return;
    }

    const url =
      this.data.get('url') ||
      target.getAttribute(`data-${this.identifier}-url`) ||
      target.getAttribute('href');

    this.bus.pub(Events.AJAX_FETCHING);
    target.setAttribute('disabled', 'disabled');

    if (this.data.has('follow') && method === 'GET') {
      Turbolinks.visit(url);
      return;
    }

    // toggle for immediate feedback
    const toggleClass = this.data.get('toggle') || 'd-none';

    this.toggleTargets.forEach((target) => {
      target.classList.toggle(toggleClass);
    });

    axios({
      headers: {
        'Turbolinks-Referrer': location.href,
      },
      method,
      url,
    })
      .then((response) => {
        const redirect = this.data.get('redirect');
        if (redirect && redirect !== 'none') {
          Turbolinks.visit(redirect);
          return;
        }

        const successMessage = response.headers['x-success-message'];

        if (successMessage) {
          this.toaster.success(successMessage);
        }

        if (this.data.has('replace')) {
          this.element.innerHTML = response.data;
          return;
        }

        if (this.data.has('remove')) {
          this.element.remove();
          return;
        }

        if (response.headers['content-type'].match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }

        this.bus.pub(Events.AJAX_COMPLETE);
      })
      .catch((err) => this.handleServerError(err))
      .finally(() => {
        target.removeAttribute('disabled');
      });
  }

  handleServerError(err) {
    this.bus.pub(Events.AJAX_COMPLETE);
    if (err.response) {
      const { status, statusText } = err.response;
      this.toaster.error(`${status}: ${statusText}`);
    }
  }
}
