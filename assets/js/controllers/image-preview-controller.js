// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Cookies from 'js-cookie';
import {
    Controller
} from 'stimulus';

export default class extends Controller {
    static targets = ['image'];

    change(event) {
        if (event.target.files) {
            const file = event.target.files[0];
            if (this.isImage(file.name)) {
                this.imageTarget.src = URL.createObjectURL(file);
                this.imageTarget.classList.remove('d-hide');
            } else {
                this.imageTarget.classList.add('d-hide');
            }
        }
    }

    isImage(url) {
        return (url.match(/\.(jpeg|jpg|gif|png)$/) != null);
    }
}