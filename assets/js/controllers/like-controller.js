import { Controller } from 'stimulus';
import axios from 'axios';

export default class extends Controller {
  like(event) {
    event.preventDefault();
    axios.post(this.data.get('url')).then(response => {
      this.element.innerText = response.data.status;
    });
  }
}
