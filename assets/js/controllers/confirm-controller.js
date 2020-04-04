// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Shows modal dialog to confirm an action. Used with ajax and confirm-dialog
  controllers.

  actions:
    check: opens modal dialog. If used in conjunction with an ajax action, place
    before in the data-action attribute e.g. data-action="confirm#check ajax#post".

  data:
    confirmed: set when the dialog returns confirmed. Do not set this yourself.
  */
  check(event) {
    // check confirmed flag, just run if set
    if (this.data.has('confirmed')) {
      this.data.delete('confirmed');
      return true;
    }
    // stop both underlying "native" event and any other events in chain
    event.preventDefault();
    event.stopImmediatePropagation();

    const header = this.data.get('header');
    const body = this.data.get('body');

    const onConfirm = () => {
      this.data.set('confirmed', true);
      // note: this doesn't work with "native" events, just with
      // stimulus events in the same data-action.
      this.element.dispatchEvent(new Event(event.type));
    };

    const dialog = document.getElementById('confirm-dialog')['confirm-dialog'];

    dialog.open({
      body,
      header,
      onConfirm,
    });

    return false;
  }
}
