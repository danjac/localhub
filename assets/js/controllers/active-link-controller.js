import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['match'];

  connect() {
    const { pathname } = window.location;
    // if element is a link i.e. <a> then just use that href
    const href =
      this.element.getAttribute('href') ||
      this.matchTarget.getAttribute('href');
    const matches = this.data.has('exact')
      ? pathname === href
      : pathname.startsWith(href);
    if (matches) {
      this.element.classList.add(this.data.get('active-class') || 'active');
    }
  }
}
