// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Events } from '~/constants';
import useTurbo from '~/utils/turbo';
import { fadeOut, maximizeZIndex } from '~/utils/dom-helpers';

import ApplicationController from './application-controller';

const TIMEOUT = 3000;

export default class extends ApplicationController {
  /*
  Used with a client rendered alert element that "fades out" after a few seconds
  after activation. Should be a single element on the page.
  */

  static targets = ['message', 'container'];
  static values = { removeAfter: Number, type: String };

  connect() {
    this.bus.sub(Events.TOAST_MESSAGE, ({ detail: { type, message } }) => {
      this.showMessage(type, message);
    });
    useTurbo(this);
  }

  turboSubmitEnd(event) {
    const { fetchResponse } = event.detail;
    const headers = fetchResponse.response ? fetchResponse.response.headers : null;
    if (!headers) {
      return;
    }

    const messages = headers.get('X-Messages');
    if (messages) {
      JSON.parse(messages).forEach((msg) => this.showMessage(msg.tags, msg.message));
    }

    const msg = headers.get('X-Message');
    const type = headers.get('X-Message-Type');
    if (msg && type) {
      this.showMessage(type, msg);
    }
  }

  showMessage(type, message) {
    this.messageTarget.innerText = message;
    // ensure any previous class is removed
    if (this.hasTypeValue) {
      this.containerTarget.classList.remove(this.typeValue);
    }
    this.containerTarget.classList.add(type);
    this.typeValue = type;

    this.element.classList.remove('hidden');
    maximizeZIndex(this.element);

    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, this.removeAfterValue || TIMEOUT);
  }

  dismiss() {
    fadeOut(this.element, () => {
      this.element.classList.add('hidden');
      // reset opacity for next message
      this.element.style.opacity = 1;
    });
  }
}
