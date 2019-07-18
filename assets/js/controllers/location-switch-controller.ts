// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  switch() {
    if (this.element instanceof HTMLInputElement) {
      this.element.disabled = true;
    }
    Turbolinks.visit(this.data.get('url'));
  }
}
