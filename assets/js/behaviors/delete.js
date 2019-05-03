import axios from 'axios';
import onmount from 'onmount';

onmount('[data-delete-from]', function() {
  // use this with data-confirm and data-confirm-trigger
  // trigger should fire confirm-delete event
  this.addEventListener('confirm-delete', event => {
    event.preventDefault();
    const { target } = event;
    const { deleteTarget, deleteFrom, redirectOnDelete } = target.dataset;
    if (deleteTarget) {
      target.closest(deleteTarget).remove();
    }
    axios.delete(deleteFrom).then(() => {
      if (redirectOnDelete) {
        window.location = redirectOnDelete;
      }
    });
  });
});
