// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { EVENT_TOAST_MESSAGE } from '@utils/application-constants';

export default class {
  constructor(controller) {
    this.controller = controller;
  }

  sendMessage(type, message) {
    this.controller.bus.publish(EVENT_TOAST_MESSAGE, { type, message });
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
