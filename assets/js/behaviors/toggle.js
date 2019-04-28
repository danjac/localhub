import onmount from 'onmount';

onmount('[data-js-toggle]', function() {
  $(this).on('click', event => {
    event.preventDefault();
    const target = $(event.currentTarget);
    $(document)
      .find(target.attr('data-js-toggle'))
      .toggleClass(target.attr('data-js-toggle-class') || 'd-none');
  });
});
