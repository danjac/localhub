// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  /*
  Turns any non-URL element into a turbolinks-enabled link

  actions:
    go: triggers the link

  data:
    url: the URL to use for the link
  */
  go(event) {
    event.preventDefault();
    this.element.disabled = true;
    Turbolinks.visit(this.data.get('url'));
  }
}
