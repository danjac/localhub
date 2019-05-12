import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

// TBD: create a single "AJAX" action controller: ("fetch-controller")
// data-controller="ajax-action"
// data-action="ajax-action#start"
// data-ajax-action-url
// data-ajax-action-method (default POST)
// data-ajax-action-redirect (override server)
// data-ajax-action-confirm-header ..-body(if absent no confirmation)
export default class extends Controller {
  confirmDelete() {
    const referrer = location.href;

    axios
      .delete(this.data.get('url'), {
        headers: {
          'Turbolinks-Referrer': referrer
        }
      })
      .then(response => {
        // override server redirect with data-delete-redirect attribute
        const redirect = this.data.get('redirect');
        if (redirect) {
          Turbolinks.visit(redirect);
        } else if (response.headers['content-type'].match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }
      })
  }

  delete(event) {
    event.preventDefault();
    this.getConfirmController().open({
      body: this.data.get('confirm-body'),
      header: this.data.get('confirm-header'),
      onConfirm: this.confirmDelete.bind(this)
    });
  }

  getConfirmController() {
    return this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm'
    );
  }


}
