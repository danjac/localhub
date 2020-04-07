// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export function openDialog(options) {
  /*
  Shortcut to open default confirmation dialog.
  options:
    header: header text
    body: body text
    onConfirm (function): callback if "confirm" button clicked.
  */
  document.getElementById('confirm-dialog')['confirm-dialog'].open(options);
}

export default class extends Controller {
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
    this.element[this.identifier] = this;
    this.onConfirm = null;
    // TBD: prob. need to remove listener in disconnect
    document.addEventListener('keydown', (event) => {
      // escape key
      if (event.keyCode === 27) {
        this.close();
      }
    });
  }

  open({ header, body, onConfirm }) {
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
    }
    this.close();
  }
}
