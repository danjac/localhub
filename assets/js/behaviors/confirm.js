import onmount from 'onmount';

onmount('[data-confirm-dialog]', function() {
  this.addEventListener('click', event => {
    const { target } = event;
    const { confirmed, confirmDialog, confirmTrigger } = target.dataset;
    if (confirmed) {
      delete target.dataset.confirmed;
      return true;
    }
    event.preventDefault();
    const dialog = document.querySelector(confirmDialog);
    dialog.classList.add('active');

    const confirmEvent = confirmTrigger
      ? new CustomEvent(confirmTrigger)
      : null;

    /* eslint-disable-next-line func-style */
    function onConfirm() {
      dialog.classList.remove('active');
      if (confirmTrigger) {
        target.dispatchEvent(confirmEvent);
      } else {
        target.dataset.confirmed = true;
        target.click();
      }
    }

    const handler = dialog.querySelector('[data-confirm-handler]');

    handler.addEventListener('click', onConfirm, { once: true });

    dialog.addEventListener('modal:close', () => {
      handler.removeEventListener('click', onConfirm, { once: true });
    });

    return false;
  });
});
