// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Controller } from 'stimulus';

let registration = null;

export default class extends Controller {
  static targets = ['subscribeBtn', 'unsubscribeBtn'];

  connect() {
    // check browser can do notifications, and permission OK.
    try {
      this.checkBrowserCompatibility();
      this.registerServiceWorker();
    } catch (e) {
      this.element.remove();
      console.log('Compatibility issue:', e.toString());
    }
  }

  registerServiceWorker() {
    const url = this.data.get('service-worker-url');

    const onRegister = swRegistration => {
      registration = swRegistration;
      return registration.pushManager.getSubscription().then(subscription => {
        if (subscription) {
          this.showUnsubscribeBtn();
        } else {
          this.showSubscribeBtn();
        }
      });
    };

    return navigator.serviceWorker.getRegistration(url).then(swRegistration => {
      if (swRegistration) {
        console.log('found existing service worker');
        return onRegister(swRegistration);
      }
      console.log('registering new service worker');
      return navigator.serviceWorker.register(url).then(onRegister);
    });
  }

  subscribe(event) {
    event.preventDefault();
    const options = {
      applicationServerKey: this.urlB64ToUint8Array(
        this.data.get('vapid-public-key')
      ),
      userVisibleOnly: true
    };
    registration.pushManager.subscribe(options).then(subscription => {
      this.showUnsubscribeBtn();
      return axios.post(
        this.data.get('subscribe-url'),
        JSON.stringify(subscription),
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    });
  }

  unsubscribe(event) {
    event.preventDefault();
    this.showSubscribeBtn();
    registration.pushManager
      .getSubscription()
      .then(subscription =>
        axios.post(
          this.data.get('unsubscribe-url'),
          JSON.stringify(subscription),
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        )
      )
      .then(registration.pushManager.unsubscribe);
  }

  showSubscribeBtn() {
    this.element.classList.remove('d-hide');
    this.subscribeBtnTarget.classList.remove('d-hide');
    this.unsubscribeBtnTarget.classList.add('d-hide');
  }

  showUnsubscribeBtn() {
    this.element.classList.remove('d-hide');
    this.unsubscribeBtnTarget.classList.remove('d-hide');
    this.subscribeBtnTarget.classList.add('d-hide');
  }

  checkBrowserCompatibility() {
    if (!('serviceWorker' in navigator)) {
      throw new Error('serviceWorker not available');
    }
    if (!('PushManager' in window)) {
      throw new Error('PushManager not available');
    }
    if (!('Notification' in window)) {
      throw new Error('Notification not available');
    }
    if (Notification.permission === 'denied') {
      throw new Error('Permission denied');
    }
  }

  urlB64ToUint8Array(base64String) {
    const mod = base64String.length % 4;
    const padding = '='.repeat((4 - mod) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i += 1) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}
