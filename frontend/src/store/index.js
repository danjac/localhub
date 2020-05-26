import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    community: null,
    messages: [],
  },
  mutations: {
    user(state, user) {
      state.user = user;
    },
    community(state, community) {
      state.community = community;
    },
    messages(state, messages) {
      state.messages = messages;
    },
    dismissMessage(state, counter) {
      state.messages.splice(counter, 1);
    },
  },
  actions: {
    // initialize app from initial data in JSON
    hydrate({ commit }, { user, community, messages }) {
      commit('user', user);
      commit('community', community);
      commit('messages', messages);
    },
    dismissMessage({ commit }, counter) {
      commit('dismissMessage', counter);
    },
  },
  modules: {},
});
