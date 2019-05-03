import axios from 'axios';
import onmount from 'onmount';

onmount('[data-delete-from]', function() {
  this.addEventListener('confirm-delete', event => {
    event.preventDefault();
    const { target } = event;
    const { deleteTarget, deleteFrom, redirectOnDelete } = target.dataset;
    target.closest(deleteTarget).remove();
    axios.delete(deleteFrom).then(() => {
      if (redirectOnDelete) {
        window.location = redirectOnDelete;
      }
    });
  });
});
