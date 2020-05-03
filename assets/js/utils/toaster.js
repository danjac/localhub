// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { EVENT_TOAST_MESSAGE } from '@utils/constants';

export default class {
  constructor(bus) {
    this.bus = bus;
  }

  sendMessage(type, message) {
    this.bus.publish(EVENT_TOAST_MESSAGE, { type, message });
  }

  success(message) {
    this.sendMessage('toast-success', message);
  }

  info(message) {
    this.sendMessage('toast-info', message);
  }

  warning(message) {
    this.sendMessage('toast-warning', message);
  }

  error(message) {
    this.sendMessage('toast-error', message);
  }
}
