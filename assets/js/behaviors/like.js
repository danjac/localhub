import axios from 'axios';
import onmount from 'onmount';

onmount('[data-like]', function() {
  this.addEventListener('click', function() {
    event.preventDefault();
    const { target } = event;
    axios.post(target.dataset.like).then(response => {
      target.text = response.data.status;
    });
  });
});
