// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later
//
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Handles client-side tab navigation. Toggles tab "active" class
  and shows/hides tab pane content accordingly.

  actions:
    select: when a specific tab is selected

  targets:
    tab: individual tab
    pane: content of a tab
  */
  static targets = ['tab', 'pane'];

  connect() {
    Array.from(this.tabTargets)[0].classList.add('active');
  }

  select(event) {
    event.preventDefault();
    const activeTab = event.currentTarget.dataset.tab;
    this.tabTargets.forEach((tab) => {
      if (tab.dataset.tab === activeTab) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    this.paneTargets.forEach((pane) => {
      if (pane.dataset.tab === activeTab) {
        pane.classList.remove('hidden');
      } else {
        pane.classList.add('hidden');
      }
    });
  }
}
