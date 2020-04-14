// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

import { openDialog } from './confirm-dialog-controller';
import { createAlert } from './alert-controller';

export default class extends Controller {
  /*
  Handles non-form AJAX interactions.

  actions:
    get: HTTP GET request
    post: HTTP POST request

  data:
    url: location of AJAX endpoint. If element has "href" attribute this
      can be used instead. This may also be placed on the action event target button.
    confirm-header: header used in confirm dialog. No confirm dialog will be triggered
      if not defined.
    confirm-body: body used in confirm dialog. No confirm dialog will be triggered
      if not defined.
    redirect: location of redirect on successful completion. This overrides any
      Location returned from the server. If "none" will not perform any redirect.
    toggle: if any toggle targets, will toggle this class (default: d-none)
    remove (bool): element will be removed when ajax action is executed.
    replace (bool): replaces inner HTML of element with HTML from response.
    follow (bool): (GET requests only) : will just redirect directly to that URL without
      calling the endpoint.

  targets:
    toggle: toggle specific items' class on successful execution.
  */

  static targets = ['toggle'];

  get(event) {
    this.confirm('GET', event);
  }

  post(event) {
    this.confirm('POST', event);
  }

  confirm(method, event) {
    event.preventDefault();
    const { currentTarget } = event;

    const onConfirm = () => {
      this.dispatch(method, currentTarget);
    };

    const header = this.data.get('confirm-header');
    const body = this.data.get('confirm-body');

    if (header && body) {
      openDialog({
        body,
        header,
        onConfirm,
      });
    } else {
      onConfirm();
    }
  }

  dispatch(method, target) {
    if (target.hasAttribute('disabled')) {
      return;
    }

    const url =
      this.data.get('url') ||
      target.getAttribute(`data-${this.data.identifier}-url`) ||
      target.getAttribute('href');

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
        const successMessage = response.headers['x-success-message'];
        if (successMessage) {
          createAlert(successMessage, 'success');
        }
        if (this.data.has('replace')) {
          this.element.innerHTML = response.data;
          return;
        }

        if (this.data.has('remove')) {
          this.element.remove();
          return;
        }

        const redirect = this.data.get('redirect');
        if (redirect) {
          if (redirect !== 'none') {
            Turbolinks.visit(redirect);
          }
          return;
        }

        if (response.headers['content-type'].match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }
      })
      .catch((err) => this.handleServerError(err))
      .finally(() => {
        target.removeAttribute('disabled');
      });
  }

  handleServerError(err) {
    if (err.response) {
      const { status, statusText } = err.response;
      const errMsg = `${status}: ${statusText}`;
      createAlert(errMsg, 'error');
    }
  }
}
