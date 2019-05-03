import onmount from 'onmount';

onmount('[data-remove-after]', function() {
  let timeout = null;
  timeout = setTimeout(() => {
    this.remove();
    clearTimeout(timeout);
  }, parseInt(this.dataset.removeAfter, 10));
});
