<template>
  <div id="app" class="h-screen container-lg mx-auto antialiased">
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
    <Footer />
  </div>
</template>

<script>
import HeaderNav from '@/components/HeaderNav.vue';
import ToastMessage from '@/components/ToastMessage.vue';
import Footer from '@/components/Footer.vue';
import SideNavLayout from '@/layouts/SideNavLayout.vue';
import SimpleLayout from '@/layouts/SimpleLayout.vue';

export default {
  components: {
    HeaderNav,
    Footer,
    ToastMessage,
  },
  computed: {
    layout() {
      return this.$store.getters.isMember ? SideNavLayout : SimpleLayout;
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
