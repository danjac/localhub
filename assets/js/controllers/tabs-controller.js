import { Controller } from 'stimulus';

export default class extends Controller {
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
        pane.classList.remove('d-none');
      } else {
        pane.classList.add('d-none');
      }
    });
  }
}
