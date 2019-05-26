import Cookies from 'js-cookie';
import { Controller } from 'stimulus';

export default class extends Controller {
  connect() {
    if (!Cookies.get('accept-cookies')) {
      this.element.classList.remove('d-hide');
    }
  }

  accept() {
    Cookies.set('accept-cookies', true, {
      domain: this.data.get('domain'),
      expires: 360
    });
    this.element.remove();
  }
}
