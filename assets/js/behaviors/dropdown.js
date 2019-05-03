import onmount from 'onmount';

onmount('[data-dropdown-toggle]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    event.target.closest('.dropdown').classList.toggle('active');
  });
});
