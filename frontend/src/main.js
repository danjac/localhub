import Vue from 'vue';
import VueI18n from 'vue-i18n';
import App from './App.vue';
import router from './router';
import store from './store';
import DefaultLayout from './layouts/Default';

import './registerServiceWorker';

import './scss/main.scss';

Vue.config.productionTip = false;

Vue.component('default-layout', DefaultLayout);
// add more layouts here...

Vue.use(VueI18n);
const i18n = new VueI18n({ locale: 'en-US' });

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app');
