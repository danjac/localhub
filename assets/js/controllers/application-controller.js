import { Controller } from 'stimulus';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  getConfirmController() {
    return this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm'
    );
  }

  redirectTo (url) {
    Turbolinks.clearCache();
    Turbolinks.visit(url);
  }
}
