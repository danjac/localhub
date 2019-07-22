// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  select() {
    const { value } = this.element;
    if (value) {
      Turbolinks.visit(value);
      this.element.disabled = true;
    }
  }
}
