import onmount from 'onmount';

onmount('[data-js-show-tab]', function() {
  $(this).on('click', event => {
    event.preventDefault();
    const target = $(event.currentTarget);
    const tabs = target.closest('.tabs');
    tabs.find('.tab-item').removeClass('active');
    tabs.find('.tab-pane').addClass('d-none');
    tabs.find(target.attr('data-js-show-tab')).removeClass('d-none');
    target.parent().addClass('active');
  });
});


