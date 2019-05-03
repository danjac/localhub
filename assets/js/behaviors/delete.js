import axios from 'axios';
import onmount from 'onmount';

import { fadeOut } from '../effects';

onmount('[data-delete-from]', function() {
  // use this with data-confirm and data-confirm-trigger
  // trigger should fire confirm-delete event
  this.addEventListener('confirm-delete', event => {
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
