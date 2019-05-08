import axios from 'axios';
import onmount from 'onmount';

import { fadeOut } from '../effects';

onmount('[data-delete-from]', function() {
  this.addEventListener('delete:confirm', event => {
    event.preventDefault();
    const { target } = event;
    const { deleteTarget, deleteFrom, redirectOnDelete } = target.dataset;
    if (deleteTarget) {
      fadeOut(target.closest(deleteTarget));
    }

    axios.delete(deleteFrom).then(() => {
      if (redirectOnDelete) {
        window.location = redirectOnDelete;
      }
    });
  });
});
