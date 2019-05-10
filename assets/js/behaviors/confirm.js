import onmount from 'onmount';

/* eslint-disable-next-line max-lines-per-function */
onmount('[data-confirm-dialog]', function() {
  this.addEventListener('click', event => {
    const { target } = event;

    const {
      confirmed,
      confirmTitle,
      confirmContent,
      confirmTrigger
    } = target.dataset;

    if (confirmed) {
      delete target.dataset.confirmed;
      return true;
    }
    event.preventDefault();
    const dialog = document.querySelector('#confirm-dialog');

    dialog.querySelector('[data-confirm-title]').innerText = confirmTitle;
    dialog.querySelector('[data-confirm-content]').innerText = confirmContent;

    const handler = dialog.querySelector('[data-confirm-handler]');
    handler.innerText = target.innerText;

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

    const listenerArgs = ['click', onConfirm, { once: true }];

    handler.addEventListener.apply(listenerArgs);

    dialog.addEventListener('modal:close', () => {
      handler.removeEventListener.apply(listenerArgs);
    });

    dialog.classList.add('active');

    return false;
  });
});
