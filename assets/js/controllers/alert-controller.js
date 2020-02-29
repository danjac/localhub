import {
  Controller
} from 'stimulus';
import {
  fadeOut
} from '../effects';

export default class extends Controller {
  connect() {
    const removeAfter = parseInt(this.data.get('remove-after') || 5000, 10);
    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, removeAfter);
  }

  dismiss() {
    fadeOut(this.element);
  }
}