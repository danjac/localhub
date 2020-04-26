// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { EVENT_CONFIRM_OPEN } from '@utils/constants';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Handles confirmation modal dialog.

  targets:
    header: header of dialog
    body: main content of dialog

  actions:
    cancel: if "cancel" button is clicked
    confirm: if "confirm" button is clicked
  */
  static targets = ['header', 'body'];

  connect() {
    // allow this to be identified by name
    // this.element[this.identifier] = this;
    document.addEventListener('keydown', (event) => {
      // escape key
      if (event.keyCode === 27) {
        this.close();
      }
    });
    this.subscribe(EVENT_CONFIRM_OPEN, (event) => this.open(event));
  }

  open({ detail: { header, body, onConfirm } }) {
    this.headerTarget.innerText = header;
    this.bodyTarget.innerText = body;
    this.onConfirm = onConfirm;
    this.element.classList.add('active');
  }

  close() {
    this.onConfirm = null;
    this.element.classList.remove('active');
  }

  cancel(event) {
    event.preventDefault();
    this.close();
  }

  confirm(event) {
    event.preventDefault();
    if (this.onConfirm) {
      this.onConfirm();
      this.onConfirm = null;
    }
    this.close();
  }
}
