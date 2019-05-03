import onmount from 'onmount';

onmount('[data-open-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    document
      .querySelector(target.dataset.openModal)
      .classList.add('active');
  });
});

onmount('[data-close-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    target.closest('.modal').classList.remove('active');
  });
});


