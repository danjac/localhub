// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export default class {
  constructor() {
    this.subscriptions = [];
  }

  pub(name, data = {}) {
    const event = new CustomEvent(name, {
      detail: Object.assign({}, data),
    });
    document.body.dispatchEvent(event);
  }

  sub(name, callback) {
    document.body.addEventListener(name, callback);
    this.subscriptions.push(() => document.body.removeEventListener(name, callback));
  }

  unsub() {
    this.subscriptions.forEach((unsub) => unsub());
  }
}
