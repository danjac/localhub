// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Events } from '@utils/constants';

export default class {
  constructor(bus) {
    this.bus = bus;
  }

  toast(type, message) {
    this.bus.pub(Events.TOAST_MESSAGE, { type, message });
  }

  success(message) {
    this.toast('message-success', message);
  }

  info(message) {
    this.toast('message-info', message);
  }

  warning(message) {
    this.toast('message-warning', message);
  }

  error(message) {
    this.toast('message-error', message);
  }
}
