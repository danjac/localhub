// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import 'leaflet/dist/leaflet.css';

import L from 'leaflet';
import { Controller } from 'stimulus';

// https://github.com/PaulLeCam/react-leaflet/issues/255

import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

/* eslint-disable-next-line no-underscore-dangle */
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl
});

const DEFAULT_ZOOM = 13;

export default class extends Controller {
  connect() {
    const coords = [this.latitude, this.longitude];
    const map = L.map(this.element.id).setView(coords, this.defaultZoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:
        'Map data &copy; <a href="https://www.openstreetmap.org/">' +
        'OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
    }).addTo(map);
    L.marker(coords).addTo(map);
  }

  get defaultZoom() {
    return parseInt(this.data.get('zoom') || DEFAULT_ZOOM, 10);
  }

  get latitude() {
    return parseFloat(this.data.get('latitude'));
  }

  get longitude() {
    return parseFloat(this.data.get('longitude'));
  }
}
