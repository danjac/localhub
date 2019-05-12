import axios from 'axios';
import Turbolinks from 'turbolinks';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['likes'];

  like(event) {
    event.preventDefault();
    axios.post(this.data.get('like-url')).then(response => {
      this.likesTarget.innerText = response.data.status;
    });
  }

  confirmDelete() {
  // TBD: we should have a generic DeleteController for this
    const referrer = location.href;

    axios
      .delete(this.data.get('delete-url'), {
        headers: {
          'Turbolinks-Referrer': referrer
        }
      })
      .then(response => {
        // if no local redirect override specified...
        eval(response.data);
      /*
        const redirect = this.data.get('delete-redirect');
        if (redirect) {
          Turbolinks.visit(redirect, { action: 'replace' });
        } else {
          Turbolinks.visit(referrer, { action: 'restore' });
        }
        */
      })
      .catch(xhr => {
        console.log('err', xhr);
      });
  }

  delete(event) {
    event.preventDefault();
    this.getConfirmController().open({
      body: this.data.get('delete-confirm-body'),
      header: this.data.get('delete-confirm-header'),
      onConfirm: this.confirmDelete.bind(this)
    });
  }
}
