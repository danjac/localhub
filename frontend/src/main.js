import axios from "axios";
import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import "./assets/main.css";

Vue.config.productionTip = false;

// axios setup
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";

(function () {
  const dataTag = document.getElementById("init-data");
  if (dataTag) {
    const initData = JSON.parse(dataTag.textContent);
    if (initData) {
      store.dispatch("hydrate", initData);
    }
  }
  return new Vue({
    router,
    store,
    render: (h) => h(App),
  }).$mount("#app");
})();
