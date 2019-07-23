// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  // make a non-URL type element into a turbolinks-enabled link
  //
  go(event) {
    event.preventDefault();
    this.element.disabled = true;
    Turbolinks.visit(this.data.get('url'));
  }
}
