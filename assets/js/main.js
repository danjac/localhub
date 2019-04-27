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

  $(document).on('log.ic', (evt, msg, level) => {
    console.log(msg, "level", level);
  });

  Intercooler.ready(function() {
    onmount();
  });

  onmount();
});
