// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

import eventBus from '@utils/event-bus';
import Toaster from '@utils/toaster';

export default class extends Controller {
  // base controller for application. All controllers should
  // subclass this.
  initialize() {
    this.subscriptions = [];
    this.toaster = new Toaster(this);
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
