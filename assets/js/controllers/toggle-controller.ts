// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* global NodeListOf */

import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['togglable'];

  togglableTargets: NodeListOf<HTMLElement>;

  toggle(event: Event) {
    event.preventDefault();
    this.togglableTargets.forEach((el: HTMLElement) =>
      el.classList.toggle('d-hide')
    );
  }
}
