import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['main', 'nav'];

  mainTarget: HTMLElement;

  navTarget: HTMLElement;

  toggle(event: Event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hide-md');
    this.navTarget.classList.toggle('hide-md');
  }
}
