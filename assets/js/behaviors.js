import onmount from 'onmount';

onmount('[data-js-open-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    document
      .getElementById(event.target.getAttribute('data-js-open-modal'))
      .classList.add('active');
  });
});

onmount('[data-js-close-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    event.target.closest('.modal').classList.remove('active');
  });
});
