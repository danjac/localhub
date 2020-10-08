// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* global require */
import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Application } from 'stimulus';

import controllers from './controllers';
import instantClick from './utils/instant-click';

// Axios setup
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// Stimulus setup
const application = Application.start();

Object.keys(controllers).forEach((name) => {
  application.register(name, controllers[name]);
});

// Instant click setup
instantClick();

// Turbolinks setup
Turbolinks.start();
