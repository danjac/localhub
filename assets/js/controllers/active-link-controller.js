import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['match'];

  connect() {
    this.matchTargets.forEach(el => {
      if (this.matches(el)) {
        el.classList.add('active');
      }
    });
  }

  matches(el) {
    const { pathname } = window.location;
    const href = el.getAttribute('href');
    if (el.hasAttribute('data-active-link-exact')) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  }
}
