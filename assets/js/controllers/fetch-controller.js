import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  send(event) {
    event.preventDefault();
    // TBD: use a "check" or "confirm" controller with data-action
    // TBD: instead of "send" have "get" , "post", "delete" etc.
    // e.g. data-controller="confirm ajax"
    // data-action="confirm#check ajax#delete"
    const header = this.data.get('confirm-header');
    const body = this.data.get('confirm-body');
    if (header && body) {
      this.getConfirmController().open({
        body,
        header,
        onConfirm: this.confirmSend.bind(this)
      });
    } else {
      this.confirmSend();
    }
  }

  confirmSend() {
    const referrer = location.href;

    const url = this.data.get('url');
    const method = this.data.get('method') || 'POST';
    const redirect = this.data.get('redirect');

    axios({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      if (this.data.has('replace')) {
        this.element.innerHTML = response.data;
      } else if (redirect) {
        Turbolinks.visit(redirect);
      } else if (response.headers['content-type'].match(/javascript/)) {
        /* eslint-disable-next-line no-eval */
        eval(response.data);
      }
    });
  }

  getConfirmController() {
    return this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm-dialog'
    );
  }
}
