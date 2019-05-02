import onmount from 'onmount';

onmount('[data-js-show-tab]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;

    const tabs = target.closest('.tabs');
    // deactivate any active tabs
    tabs
      .querySelectorAll('.tab-item')
      .forEach(tab => tab.classList.remove('active'));
    tabs
      .querySelectorAll('.tab-pane')
      .forEach(tab => tab.classList.add('d-none'));

    // activate selected tab
    tabs
      .querySelector(target.dataset.jsShowTab)
      .classList.remove('d-none');

    target.parentNode.classList.add('active');
  });
});
