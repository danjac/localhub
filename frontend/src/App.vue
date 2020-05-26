<template>
  <div id="app">
    <HeaderNav />
    <component :is="layout" class="mt-5">
      <router-view />
    </component>
  </div>
</template>

<script>
import HeaderNav from './components/HeaderNav.vue';
import SideNavLayout from './layouts/SideNavLayout.vue';
import SimpleLayout from './layouts/SimpleLayout.vue';

export default {
  components: {
    HeaderNav,
  },
  computed: {
    layout() {
      // TBD: we need "is_member" in the store to determine user membership....
      return this.$store.state.user && this.$store.state.community
        ? SideNavLayout
        : SimpleLayout;
    },
  },
};
</script>
