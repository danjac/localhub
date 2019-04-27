import onmount from 'onmount';
import Intercooler from 'intercooler';

import './behaviors';

import { csrfSafeMethod, getCookie } from './utils';

$(function() {
  $(document).on('beforeAjaxSend.ic', (event, ajaxSetup) => {
    if (!csrfSafeMethod(ajaxSetup.type)) {
      ajaxSetup.headers['X-CSRFToken'] = getCookie('csrftoken');
    }
  });

  Intercooler.ready(function() {
    onmount();
  });

  onmount();
});
