// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import '@hotwired/turbo';

import { Application } from 'stimulus';
import { definitionsFromContext } from 'stimulus/webpack-helpers';

import instantClick from './utils/instant-click';

// Stimulus setup
const application = Application.start();
const context = require.context('./controllers', true, /\.js$/);
application.load(definitionsFromContext(context));

// Instant click setup
instantClick();
