import { Controller } from 'stimulus';
import { fadeOut } from '../effects';

export default class extends Controller {
  timeout: any;

  connect() {
    const removeAfter = this.data.get('remove-after');
    const delay = removeAfter ? parseInt(removeAfter, 10) : 5000;
    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, delay);
  }

  dismiss() {
    if (this.element instanceof HTMLElement) {
      fadeOut(this.element);
    }
  }
}
