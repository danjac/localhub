import axios from 'axios';
import Turbolinks from 'turbolinks';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  submit(event) {
    event.preventDefault();
    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');
    const referrer = location.href;

    axios({
      data: this.serialize(),
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      const contentType = response.headers['content-type'];
      // errors in form, re-render
      if (contentType.match(/html/)) {
        Turbolinks.controller.cache.put(
          referrer,
          Turbolinks.Snapshot.wrap(response.data)
        );
        Turbolinks.visit(referrer, { action: 'restore' });
      } else if (contentType.match(/javascript/)) {
        /* eslint-disable-next-line no-eval */
        eval(response.data);
      }
    });
  }

  // https://vanillajstoolkit.com/helpers/serialize/
  //

  serialize() {
    const serialized = [];

    for (let i = 0; i < this.element.elements.length; i += 1) {
      const field = this.element.elements[i];
      if (!this.serializable(field)) {
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
  }

  serializable(field) {
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
  }
}
