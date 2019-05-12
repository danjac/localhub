import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  send(event) {
    event.preventDefault();
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
    // TBD: "replace" if we just want to insert content
    // this.element.innerHTML = response.data

    axios({
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      if (redirect) {
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
      'confirm'
    );
  }
}
