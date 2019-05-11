import axios from 'axios';
import { fadeOut } from '../effects';
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
    fadeOut(this.element);
    axios.delete(this.data.get('delete-url'));
  }

  delete(event) {
    event.preventDefault();
    this.getConfirmController().open({
      body: this.data.get("delete-confirm-body"),
      header: this.data.get("delete-confirm-header"),
      onConfirm: this.confirmDelete.bind(this)
    });
  }
}
