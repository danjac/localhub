import onmount from 'onmount';

onmount('[data-confirm-dialog]', function() {
  this.addEventListener('click', event => {
    const { target } = event;
    const { confirmed, confirmDialog, confirmTriggerOn } = target.dataset;
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
        if (confirmTriggerOn) {
          target.dispatchEvent(new CustomEvent(confirmTriggerOn));
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
