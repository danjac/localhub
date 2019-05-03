import onmount from 'onmount';

onmount('[data-toggle]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    const { toggle, toggleClass } = target.dataset;
    document.querySelector(toggle).classList.toggle(toggleClass || 'd-none');
  });
});
