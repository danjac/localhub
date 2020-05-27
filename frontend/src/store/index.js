import Vue from 'vue';
import Vuex from 'vuex';
import { uniqueId } from 'lodash';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    community: null,
    messages: [],
    showNav: false,
  },
  mutations: {
    user(state, user) {
      state.user = user;
    },
    community(state, community) {
      state.community = community;
    },
    addMessage(state, msg) {
      state.messages.push({ ...msg, id: uniqueId() });
    },
    dismissMessage(state, msgId) {
      state.messages = state.messages.filter((msg) => msg.id != msgId);
    },
    toggleNav(state) {
      state.showNav = !state.showNav;
    },
    closeNav(state) {
      state.showNav = false;
    },
  },
  actions: {
    // initialize app from initial data in JSON
    hydrate({ commit }, { user, community, messages }) {
      commit('user', user);
      commit('community', community);
      messages.forEach((msg) => commit('addMessage', msg));
    },
    addMessage({ commit }, msg) {
      commit('addMessage', msg);
    },
    dismissMessage({ commit }, counter) {
      commit('dismissMessage', counter);
    },
    toggleNav({ commit }) {
      commit('toggleNav');
    },
    closeNav({ commit }) {
      commit('closeNav');
    },
  },
  getters: {
    isMember(state) {
      return (
        !!state.user &&
        !!state.community &&
        state.community.active &&
        !!state.user.roles[state.community.id]
      );
    },
    isModerator(state) {
      return (
        state.user &&
        state.community &&
        state.community.active &&
        ['moderator', 'admin'].includes(state.user.roles[state.community.id])
      );
    },
    isAdmin(state) {
      return (
        state.user &&
        state.community &&
        state.community.active &&
        state.user.roles[state.community.id] === 'admin'
      );
    },
  },
  modules: {},
});
