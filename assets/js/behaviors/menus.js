import onmount from 'onmount';

onmount('[data-js-dropdown-toggle]', function() {
  $(this).on('click', event => {
    event.preventDefault();
    $(event.currentTarget)
      .closest('.dropdown')
      .toggleClass('active');
  });
});
