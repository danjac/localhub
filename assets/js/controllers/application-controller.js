// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

import eventBus from '@utils/event-bus';
import Dialog from '@utils/dialog';
import Toaster from '@utils/toaster';

export default class extends Controller {
  // base controller for application. All controllers should
  // subclass this.
  initialize() {
    this.subscriptions = [];
    this.toaster = new Toaster(this);
    this.dialog = new Dialog(this);
  }

  publish(name, data) {
    eventBus.publish(name, data);
  }

  subscribe(name, callback) {
    this.subscriptions.push(eventBus.subscribe(name, callback));
  }

  unsubscribe() {
    this.subscriptions.forEach((unsub) => unsub());
  }

  disconnect() {
    this.unsubscribe();
  }
}
