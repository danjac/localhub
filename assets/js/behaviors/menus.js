import onmount from 'onmount';

onmount('[data-js-dropdown-toggle]', function() {
  $(this).on('click', event => {
    event.preventDefault();
    const target = $(event.currentTarget);
    target.closest('.dropdown').toggleClass('active');
  });
});
