import onmount from 'onmount';

onmount('[data-js-open-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    document
      .querySelector(target.getAttribute('data-js-open-modal'))
      .classList.add('active');
  });
});

onmount('[data-js-close-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    target.closest('.modal').classList.remove('active');
  });
});


