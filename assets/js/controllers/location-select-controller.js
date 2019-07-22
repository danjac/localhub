// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  select() {
    const { value } = this.element;
    if (value) {
      window.location.href = value;
      this.element.disabled = true;
    }
  }
}
