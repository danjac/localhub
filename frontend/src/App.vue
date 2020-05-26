<template>
  <div id="app">
    <HeaderNav />

    <ToastMessage
      v-for="(message, counter) in messages"
      :key="counter"
      :message="message"
      class="mb-2"
      @dismiss="dismissMessage(counter)"
    />

    <component :is="layout" class="mt-5">
      <router-view />
    </component>
  </div>
</template>

<script>
import HeaderNav from './components/HeaderNav.vue';
import ToastMessage from './components/ToastMessage.vue';
import SideNavLayout from './layouts/SideNavLayout.vue';
import SimpleLayout from './layouts/SimpleLayout.vue';

export default {
  components: {
    HeaderNav,
    ToastMessage,
  },
  computed: {
    layout() {
      // TBD: we need "is_member" in the store to determine user membership....
      return this.$store.state.user && this.$store.state.community
        ? SideNavLayout
        : SimpleLayout;
    },
    messages() {
      return this.$store.state.messages;
    },
  },
  methods: {
    dismissMessage(counter) {
      this.$store.dispatch('dismissMessage', counter);
    },
  },
};
</script>
