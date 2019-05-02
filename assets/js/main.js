import onmount from 'onmount';

import './behaviors';

import { csrfSafeMethod, getCookie } from './utils';

$(function() {
  // we'll throw in axios later, one thing at a time
  $.ajaxSetup({
    beforeSend(xhr, settings) {
      if (!csrfSafeMethod(settings.type)) {
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
      }
    }
  });
  onmount();
});
