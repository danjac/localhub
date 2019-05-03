import onmount from 'onmount';

import { fadeOut } from '../effects';

onmount('[data-remove-after]', function() {
  let timeout = null;
  timeout = setTimeout(() => {
    fadeOut(this);
    clearTimeout(timeout);
  }, parseInt(this.dataset.removeAfter, 10));
});
