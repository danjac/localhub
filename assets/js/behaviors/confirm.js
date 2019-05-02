import onmount from 'onmount';

onmount('[data-js-confirm-dialog]', function() {
  this.addEventListener('click', event => {
    const { target } = event;
    if (target.hasAttribute('data-confirmed')) {
      target.removeAttribute('data-confirmed');
      return true;
    }
    event.preventDefault();
    const dialog = document.querySelector(
      target.getAttribute('data-js-confirm-dialog')
    );
    dialog.classList.add('active');
    dialog.querySelector('[data-js-confirm-dialog-handler]').addEventListener(
      'click',
      () => {
        dialog.classList.remove('active');
        const trigger = target.getAttribute('data-js-confirm-trigger');
        if (trigger) {
          target.dispatchEvent(new CustomEvent(trigger));
        } else {
          target.setAttribute('data-confirmed', true);
          target.click();
        }
      },
      { once: true }
    );
    return false;
  });
});
