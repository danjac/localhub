// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
    Controller
} from 'stimulus';

import Turbolinks from 'turbolinks';

export default class extends Controller {
    static targets = ['input', 'selector'];

    connect() {
        this.toggleSelector();
        const {
            pathname
        } = window.location;
        for (const option of this.selectorTarget.options) {
            if (option.value === pathname) {
                option.setAttribute('selected', true);
            }
        }
    }

    change() {
        this.toggleSelector();
    }

    select() {
        const {
            value
        } = this.selectorTarget;
        const param = this.data.get('param') || 'q';
        const search = this.inputTarget.value;
        if (value && search) {
            Turbolinks.visit(`${value}?${param}=${search}`);
        }
    }

    toggleSelector() {
        if (!!this.inputTarget.value) {
            this.selectorTarget.removeAttribute('disabled');
        } else {
            this.selectorTarget.setAttribute('disabled', true);
        }
    }
}