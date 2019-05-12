import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  submit(event) {
    event.preventDefault();
    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');
    const referrer = location.href;

    const data = this.serialize();

    this.element
      .querySelectorAll('input,textarea')
      .forEach(el => el.setAttribute('disabled', true));

    if (method === "GET") {
      return Turbolinks.visit(`${url}?${data}`)
    }

    axios({
      data,
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      this.element
        .querySelectorAll('input,textarea')
        .forEach(el => el.removeAttribute('disabled'));
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
  // use FormData for multipart forms?

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
    // allow file type if multipart...
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
