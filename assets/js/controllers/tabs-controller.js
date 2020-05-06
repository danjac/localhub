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
    const tabs = Array.from(this.tabTargets);
    this.addClassnames(tabs[0], this.data.get('active-class'));
    tabs
      .slice(1)
      .forEach((tab) => this.addClassnames(tab, this.data.get('inactive-class')));
  }

  select(event) {
    event.preventDefault();
    const activeTab = event.currentTarget.dataset.tab;
    this.tabTargets.forEach((tab) => {
      if (tab.dataset.tab === activeTab) {
        this.addClassnames(tab, this.data.get('active-class'));
        this.removeClassnames(tab, this.data.get('inactive-class'));
      } else {
        this.addClassnames(tab, this.data.get('inactive-class'));
        this.removeClassnames(tab, this.data.get('active-class'));
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

  addClassnames(el, classnames) {
    el.classList.add.apply(el.classList, classnames.split(/ /));
  }

  removeClassnames(el, classnames) {
    el.classList.remove.apply(el.classList, classnames.split(/ /));
  }
}
