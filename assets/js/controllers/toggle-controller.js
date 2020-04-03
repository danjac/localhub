// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Toggles one or more elements using d-hide class.

  actions:
    toggle: toggles d-hide on all togglable targets. The trigger element
      should include a data-toggle-target attribute which specifies the
      element(s) to be toggled.

  targets:
    togglable: an element to be toggled. Element should also have a
    data-toggle-target element that identifies target of toggle.
  */
  static targets = ['togglable'];

  toggle(event) {
    event.preventDefault();

    const targetAttr = `data-${this.data.identifier}-target`;
    const target = event.currentTarget.getAttribute(targetAttr);

    this.togglableTargets
      .filter(el => el.getAttribute(targetAttr) === target)
      .forEach(el => el.classList.toggle('d-hide'));
  }
}
