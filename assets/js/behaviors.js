import onmount from 'onmount';

onmount('[data-js-show-tab]', function() {
  $(this).on('click', event => {
    const target = $(event.currentTarget);
    const tabs = target.closest('.tabs');
    tabs.find('.tab-item').removeClass('active');
    tabs.find('.tab-pane').addClass('d-none');
    tabs.find(target.attr('data-js-show-tab')).removeClass('d-none');
    target.parent().addClass('active');
  });
});

onmount('[data-js-confirm-dialog]', function() {
  $(this).on('click', event => {
    const target = $(event.currentTarget);
    if (target.data('confirmed')) {
      target.removeData('confirmed');
      return true;
    }
    event.preventDefault();
    const dialog = $(target.attr('data-js-confirm-dialog')).addClass('active');
    dialog.find('[data-js-confirm-dialog-handler]').one('click', () => {
      dialog.removeClass('active');
      if (target.attr('data-ic-trigger-on')) {
        target.trigger(target.attr('data-ic-trigger-on'));
      } else {
        target.data('confirmed', true);
        target.trigger('click');
      }
    });
    return false;
  });
});

onmount('[data-js-open-modal]', function() {
  $(this).on('click', () => {
    event.preventDefault();
    $($(event.currentTarget).attr('data-js-open-modal')).addClass('active');
  });
});

onmount('[data-js-close-modal]', function() {
  $(this).on('click', () => {
    event.preventDefault();
    $(event.currentTarget)
      .closest('.modal')
      .removeClass('active');
  });
});
