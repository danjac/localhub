<template>
  <div id="app" class="h-screen container-lg mx-auto antialiased">
    <HeaderNav />

    <div class="flex justify-center" v-if="messages">
      <ToastMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
        class="mb-2"
        @dismiss="dismissMessage(message.id)"
      />
    </div>

    <component class="mt-5" :is="layout">
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
    isMember() {
      return this.$store.getters.isMember;
    },
    isModerator() {
      return this.$store.getters.isModerator;
    },
    isAdmin() {
      return this.$store.getters.isAdmin;
    },
  },
  methods: {
    dismissMessage(msgId) {
      this.$store.dispatch('dismissMessage', msgId);
    },
  },
};
</script>
