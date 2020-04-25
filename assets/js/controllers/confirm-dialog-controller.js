// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

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
    const open = (data) => console.log(data);
    this.subscribe('confirm:open', open);
  }

  open({ header, body }) {
    this.headerTarget.innerText = header;
    this.bodyTarget.innerText = body;
    this.element.classList.add('active');
  }

  close() {
    this.element.classList.remove('active');
  }

  cancel(event) {
    event.preventDefault();
    this.close();
  }

  confirm(event) {
    event.preventDefault();
    this.publish('confirm:done');
    this.close();
  }
}
