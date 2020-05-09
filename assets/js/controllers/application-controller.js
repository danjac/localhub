// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

import { ClassList } from '@utils/class-list';
import EventBus from '@utils/event-bus';
import Toaster from '@utils/toaster';

export default class extends Controller {
  // base controller for application. All controllers should
  // subclass this.
  initialize() {
    this.bus = new EventBus();
    this.toaster = new Toaster(this.bus);
    this.classList = new ClassList(this.element);
  }

  disconnect() {
    this.bus.unsub();
  }
}
