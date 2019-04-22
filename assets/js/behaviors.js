import onmount from 'onmount';

onmount('[data-js-confirm-dialog]', function() {
  this.addEventListener('click', event => {
    const { target } = event;
    if (target.hasAttribute('data-js-confirm-dialog-confirmed')) {
      target.removeAttribute('data-js-confirm-dialog-confirmed');
      return true;
    }
    event.preventDefault();

    const dialog = document.getElementById(
      target.getAttribute('data-js-confirm-dialog')
    );
    dialog.classList.add('active');

    dialog.querySelector('[data-js-confirm-dialog-handler]').addEventListener(
      'click',
      () => {
        dialog.classList.remove('active');
        if (target.hasAttribute('data-ic-trigger-on')) {
          //
          // this might not work depending on how Intercooler does the event
          // handling; might need to wrap in jQuery i.e.
          // $(target).trigger('event-name');
          target.dispatchEvent(
            new Event(target.getAttribute('data-ic-trigger-on'))
          );
        } else {
          target.setAttribute('data-js-confirm-dialog-confirmed', true);
          target.click();
        }
      },
      { once: true }
    );
    return false;
  });
});

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
