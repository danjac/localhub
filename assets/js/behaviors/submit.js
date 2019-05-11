import onmount from 'onmount';
import axios from 'axios';
import Turbolinks from 'turbolinks';

// https://vanillajstoolkit.com/helpers/serialize/
//

const serializable = field => {
  if (
    !field.name ||
    field.disabled ||
    field.type === 'file' ||
    field.type === 'reset' ||
    field.type === 'submit' ||
    field.type === 'button'
  ) {
    return false;
  }
  return true;
};

const serialize = form => {
  const serialized = [];

  for (let i = 0; i < form.elements.length; i += 1) {
    const field = form.elements[i];
    if (!serializable(field)) {
      continue;
    }

    if (field.type === 'select-multiple') {
      for (let n = 0; n < field.options.length; n += 1) {
        if (!field.options[n].selected) {
          continue;
        }
        serialized.push(
          encodeURIComponent(field.name) +
            '=' +
            encodeURIComponent(field.options[n].value)
        );
      }
    } else if (
      (field.type !== 'checkbox' && field.type !== 'radio') ||
      field.checked
    ) {
      // Convert field data to a query string
      serialized.push(
        encodeURIComponent(field.name) + '=' + encodeURIComponent(field.value)
      );
    }
  }

  return serialized.join('&');
};

onmount('[data-turbolinks-submit]', function() {
  this.addEventListener('submit', event => {
    event.preventDefault();

    const { target } = event;
    const method = target.getAttribute('method');
    const url = target.getAttribute('action');
    const referrer = location.href;

    axios({
      data: serialize(target),
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      if (response.headers['content-type'].match(/html/)) {
        Turbolinks.controller.cache.put(
          referrer,
          Turbolinks.Snapshot.wrap(response.data)
        );
        Turbolinks.visit(referrer, { action: 'restore' });
      }
    });
  });
});
