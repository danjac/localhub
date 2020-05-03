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
    this.toast('toast-success', message);
  }

  info(message) {
    this.toast('toast-info', message);
  }

  warning(message) {
    this.toast('toast-warning', message);
  }

  error(message) {
    this.toast('toast-error', message);
  }
}
