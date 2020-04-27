// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { EVENT_TOAST_MESSAGE } from '@utils/application-constants';
import { fadeOut } from '@utils/dom-helpers';

import ApplicationController from './application-controller';

const TIMEOUT = 3000;

export default class extends ApplicationController {
  /*
  Used with a client rendered alert element that "fades out" after a few seconds
  after activation. Should be a single element on the page.

  data:
    remove-after: number of milliseconds (default: 5000)

  targets:
    message: container element for message

  actions:
    dismiss
  */

  static targets = ['message'];

  connect() {
    this.subscribe(EVENT_TOAST_MESSAGE, ({ detail: { type, message } }) => {
      this.showMessage(type, message);
    });
  }

  showMessage(type, message) {
    this.messageTarget.innerText = message;
    this.element.classList.add(type);
    this.element.classList.remove('d-none');

    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, this.removeAfter);
  }

  dismiss() {
    fadeOut(this.element, () => {
      this.element.classList.add('d-none');
      // reset opacity for next message
      this.element.style.opacity = 1;
    });
  }

  get removeAfter() {
    return parseInt(this.data.get('remove-after') || TIMEOUT, 10);
  }
}
