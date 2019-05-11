/* global require */
import axios from 'axios';
// import onmount from 'onmount';
import Turbolinks from 'turbolinks';

import { Application } from 'stimulus';
import { definitionsFromContext } from 'stimulus/webpack-helpers';

// import './behaviors';

axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

/*
axios.interceptors.response.use(data => {
  onmount();
  return data;
});

document.addEventListener('DOMContentLoaded', () => {
  onmount();
});

document.addEventListener('turbolinks:load', () => {
  onmount();
});
*/

// Stimulus setup
const application = Application.start();
const context = require.context('./controllers', true, /\.js$/);
application.load(definitionsFromContext(context));

// Turbolinks setup
Turbolinks.start();

