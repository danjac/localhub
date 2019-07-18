import { Controller } from 'stimulus';

import { HTMLElementEvent } from '../types';

/* global NodeListOf */

export default class extends Controller {
  static targets = ['tab', 'pane'];

  paneTargets: NodeListOf<HTMLElement>;

  tabTargets: NodeListOf<HTMLElement>;

  select(event: HTMLElementEvent) {
    event.preventDefault();
    const activeTab = event.currentTarget.dataset.tab;
    this.tabTargets.forEach((tab: HTMLElement) => {
      if (tab.dataset.tab === activeTab) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    this.paneTargets.forEach((pane: HTMLElement) => {
      if (pane.dataset.tab === activeTab) {
        pane.classList.remove('d-none');
      } else {
        pane.classList.add('d-none');
      }
    });
  }
}
