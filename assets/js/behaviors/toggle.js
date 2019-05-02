import onmount from 'onmount';

onmount('[data-js-toggle]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    document
      .querySelector(target.getAttribute('data-js-toggle'))
      .classList.toggle(
        target.getAttribute('data-js-toggle-class') || 'd-none'
      );
  });
});
