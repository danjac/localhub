// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

import EventBus from '@utils/event-bus';
import Toaster from '@utils/toaster';

export default class extends Controller {
  // base controller for application. All controllers should
  // subclass this.
  initialize() {
    this.bus = new EventBus();
    this.toaster = new Toaster(this.bus);
  }

  disconnect() {
    this.bus.unsub();
  }
}
