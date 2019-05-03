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
    dialog.querySelector('[data-confirm-handler]').addEventListener(
      'click',
      () => {
        dialog.classList.remove('active');
        if (confirmTrigger) {
          target.dispatchEvent(new CustomEvent(confirmTrigger));
        } else {
          target.dataset.confirmed = true;
          target.click();
        }
      },
      { once: true }
    );
    return false;
  });
});
