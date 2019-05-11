import { Controller } from 'stimulus';

export default class extends Controller {
  getConfirmController() {
    return this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm'
    );
  }
}
