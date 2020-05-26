<template>
  <div class="px-2 md:px-5 flex min-h-full">
    <SideNav :class="{ hidden: !showNav }" />
    <div class="lg:ml-2 w-full lg:w-5/6 lg:block" :class="{ hidden: showNav }">
      <slot />
    </div>
  </div>
</template>

<script>
import SideNav from '@/components/SideNav.vue';

export default {
  components: {
    SideNav,
  },
  computed: {
    showNav() {
      return this.$store.state.showNav;
    },
  },
};
</script>
