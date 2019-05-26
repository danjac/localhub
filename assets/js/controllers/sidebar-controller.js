import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['main', 'nav', 'match', 'exactMatch'];

  connect() {
    const { pathname } = window.location;
    this.matchTargets.forEach(el => {
      if (pathname.startsWith(el.getAttribute('href'))) {
        el.classList.add('active');
      }
    });
    this.exactMatchTargets.forEach(el => {
      if (el.getAttribute('href') === pathname) {
        el.classList.add('active');
      }
    });
  }

  toggle(event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hide-sm');
    this.navTarget.classList.toggle('hide-sm');
  }
}
