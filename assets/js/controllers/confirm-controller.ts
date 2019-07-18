// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import Openable from './confirm-dialog-controller';

export default class extends Controller {
  check(event: Event): Boolean {
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
      this.data.set('confirmed', 'confirmed');
      // note: this doesn't work with "native" events, just with
      // stimulus events in the same data-action.
      this.element.dispatchEvent(new Event(event.type));
    };

    const dialog = this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm-dialog'
    );

    if (dialog instanceof Openable) {
      dialog.open({
        body,
        header,
        onConfirm
      });
    }

    return false;
  }
}
