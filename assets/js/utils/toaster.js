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
    this.toast('bg-green-800', message);
  }

  info(message) {
    this.toast('bg-blue-600', message);
  }

  warning(message) {
    this.toast('bg-orange-600', message);
  }

  error(message) {
    this.toast('bg-red-600', message);
  }
}
