import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['header', 'body'];

  initialize() {
    this.onConfirm = null;
    document.addEventListener('keydown', event => {
      // escape key
      if (event.keyCode === 27) {
        this.close();
      }
    });
  }

  open(options) {
    const { header, body, onConfirm } = options;
    this.headerTarget.innerText = header;
    this.bodyTarget.innerText = body;
    this.onConfirm = onConfirm;
    this.element.classList.add('active');
  }

  close() {
    this.onConfirm = null;
    this.element.classList.remove('active');
  }

  cancel(event) {
    event.preventDefault();
    this.close();
  }

  confirm(event) {
    event.preventDefault();
    if (this.onConfirm) {
      this.onConfirm();
    }
    this.close();
  }
}
