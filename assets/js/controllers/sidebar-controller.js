import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['main', 'nav'];

  toggle(event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hide-md');
    this.navTarget.classList.toggle('hide-md');
  }
}
