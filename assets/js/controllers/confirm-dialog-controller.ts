// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

interface Confirmable {
  header: string,
  body: string,
  onConfirm(): void
}

interface Openable {
  open(config: Confirmable): void
}

export default class extends Controller implements Openable {
  static targets = ['header', 'body'];

  headerTarget: HTMLElement;

  bodyTarget: HTMLElement;

  onConfirm: Function;

  connect() {
    this.onConfirm = null;
    // TBD: prob. need to remove listener in disconnect
    document.addEventListener('keydown', event => {
      // escape key
      if (event.keyCode === 27) {
        this.close();
      }
    });
  }

  open({ header, body, onConfirm }: Confirmable) {
    this.headerTarget.innerText = header;
    this.bodyTarget.innerText = body;
    this.onConfirm = onConfirm;
    this.element.classList.add('active');
  }

  close() {
    this.onConfirm = null;
    this.element.classList.remove('active');
  }

  cancel(event: Event) {
    event.preventDefault();
    this.close();
  }

  confirm(event: Event) {
    event.preventDefault();
    if (this.onConfirm) {
      this.onConfirm();
    }
    this.close();
  }
}
