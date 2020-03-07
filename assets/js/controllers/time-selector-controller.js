// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later
import {
    Controller
} from 'stimulus';

export default class extends Controller {
    static targets = ["selector", "hour", "minute", "timeInput"]
    toggle(event) {
        event.preventDefault();
        if (!this.selectorTarget.classList.toggle('d-none')) {
            this.render();
        }
    }

    select() {
        event.preventDefault();
        this.timeInputTarget.value = [
            this.hourTarget.value, this.minuteTarget.value
        ].map(value => this.pad(value, 2)).join(":");
        this.selectorTarget.classList.add('d-none');
    }

    render() {

        const [selectedHour, selectedMinute] = (
            this.timeInputTarget.value || this.data.get('default') || '9:00'
        ).split(':').map(value => parseInt(value, 10));

        // hours
        for (let hour = 0; hour < 24; ++hour) {
            this.createOption(
                this.hourTarget,
                hour,
                this.pad(hour, 2),
                selectedHour
            )
        }

        // minutes
        for (let minute = 0; minute < 59; minute += 5) {
            this.createOption(
                this.minuteTarget,
                minute,
                this.pad(minute, 2),
                selectedMinute
            )
        }
    }
    createOption(select, value, text, selectedValue) {
        const option = document.createElement("option");
        option.value = value;
        option.append(text);
        if (value === selectedValue) {
            option.setAttribute("selected", true);
        }
        select.append(option);
    }

    pad(n, width) {
        // convert to string
        n = n + '';
        return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
    }
}