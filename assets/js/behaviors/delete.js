import axios from 'axios';
import onmount from 'onmount';

onmount('[data-js-delete]', function() {
  this.addEventListener('confirm-delete', event => {
    event.preventDefault();
    const { target } = event;
    const { jsDeleteTarget, jsDelete } = target.dataset;
    target.closest(jsDeleteTarget).remove();
    axios.delete(jsDelete);
  });
});
