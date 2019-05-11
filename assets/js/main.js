import axios from 'axios';
import onmount from 'onmount';
import Turbolinks from 'turbolinks';

import './behaviors';

axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

axios.interceptors.response.use(data => {
  // TBD: use custom events to handle errors and server-side messages
  onmount();
  return data;
});

document.addEventListener('DOMContentLoaded', () => {
  onmount();
});

document.addEventListener('turbolinks:load', () => {
  onmount();
});

Turbolinks.start();
