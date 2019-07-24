import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['main', 'nav'];

  toggle(event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hide-lg');
    this.navTarget.classList.toggle('hide-lg');
  }
}
