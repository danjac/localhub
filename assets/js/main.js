// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* global require */
import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Application } from 'stimulus';
import { definitionsFromContext } from 'stimulus/webpack-helpers';

// Axios setup
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// Stimulus setup
const application = Application.start();
const context = require.context('./controllers', true, /\.(js|ts)$/);
application.load(definitionsFromContext(context));

// Turbolinks setup
Turbolinks.start();
