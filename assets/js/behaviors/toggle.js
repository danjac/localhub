import onmount from 'onmount';

onmount('[data-toggle]', function() {
  this.addEventListener('click', event => {
    console.log('data-toggle');
    event.preventDefault();
    const { target } = event;
    const { toggle, toggleClass } = target.dataset;
    document
      .querySelectorAll(toggle)
      .forEach(el => el.classList.toggle(toggleClass || 'd-none'));
  });
});
