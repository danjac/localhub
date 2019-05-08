import onmount from 'onmount';

const closeModalEvent = new CustomEvent('modal:close');

const closeModal = () => {
  const modal = document.querySelector('.modal.active');
  if (modal) {
    modal.classList.remove('active');
    modal.dispatchEvent(closeModalEvent);
  }
};

onmount('[data-open-modal]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    document.querySelector(target.dataset.openModal).classList.add('active');
  });
});

onmount('[data-close-modal]', function() {
  document.addEventListener('keydown', event => {
    // escape key
    if (event.keyCode === 27) {
      closeModal();
    }
  });

  this.addEventListener('click', event => {
    event.preventDefault();
    closeModal();
  });
});
